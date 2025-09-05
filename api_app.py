import os
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

from dotenv import load_dotenv
from io import BytesIO

from TARS.graph import make_graph
from T2S_S2T.text_2_speech import add_tars_pauses
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from openai import OpenAI
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# === Setup ===
load_dotenv()
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure folders exist
os.makedirs("equations", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Serve static files (so frontend can fetch them directly)
app.mount("/equations", StaticFiles(directory="equations"), name="equations")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Init APIs
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key=os.getenv("XI_API_KEY"))

# Build LangGraph once
checkpointer = InMemorySaver()
graph = make_graph(checkpointer=checkpointer)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask")
async def ask(audio: UploadFile = File(...)):
    """
    Accepts an audio file, transcribes it, runs TARS agent, 
    saves ElevenLabs audio reply, returns JSON with transcript, text, audio, equations.
    """
    try:
        # 1. Clear equations from previous run
        for f in os.listdir("equations"):
            os.remove(os.path.join("equations", f))

        # 2. Read uploaded audio file into memory
        audio_bytes = await audio.read()

        # 3. Transcribe with Whisper
        file_like = BytesIO(audio_bytes)
        file_like.name = audio.filename or "audio.webm"  # give it a name for the SDK
        
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=file_like,
        )
        transcript_text = transcription.text

        # 4. Run TARS graph with transcription
        convo_id = str(uuid.uuid4())[:8]
        result = graph.invoke(
            {"messages": [HumanMessage(content=transcript_text)]},
            {"configurable": {"thread_id": convo_id}, "recursion_limit": 45},
        )
        tars_text = result["messages"][-1].content

        # 5. Generate TTS audio with ElevenLabs
        text = tars_text.replace("Dr.", "doctor").replace("dr.", "doctor").replace("prof.", "professor").replace("Prof.", "professor")
        cleaned_text = text.replace("**", "").replace("$", "").replace("/", "").replace("{", "").replace("}", "").replace("/", "")  
        paused_text = add_tars_pauses(cleaned_text)        

        response = elevenlabs_client.text_to_speech.convert(
            voice_id="dNXy174F4uFM8G0CUjYL",  # TARS-like voice
            output_format="mp3_22050_32",
            text=paused_text,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                speed=0.98,
                stability=0.82,
                similarity_boost=0.98,
                style=0.0,
                use_speaker_boost=False,
            ),
        )

        # Save audio file
        run_id = str(uuid.uuid4())[:8]
        audio_path = f"outputs/response_{run_id}.mp3"
        with open(audio_path, "wb") as f:
            for chunk in response:          # <-- write the streaming chunks
                if chunk:
                    f.write(chunk)

        # 6. Collect equations
        equations = []
        for fname in os.listdir("equations"):
            with open(os.path.join("equations", fname), "r") as f:
                equations.append({
                    "filename": fname,
                    "content": f.read()
                })

        # 7. Return JSON
        return JSONResponse({
            "transcript": transcript_text,
            "text": tars_text,
            "audio_url": f"/outputs/{os.path.basename(audio_path)}",
            "equations": equations
        })

    except Exception as e:
        # Log server-side
        import traceback; traceback.print_exc()
        # Return clean error to the client
        raise HTTPException(status_code=500, detail=str(e))
