import os
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from TARS.graph import make_graph
from TARS.state import TARSState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from openai import OpenAI
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# === Setup ===
load_dotenv()
app = FastAPI()

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

    # 1. Clear equations from previous run
    for f in os.listdir("equations"):
        os.remove(os.path.join("equations", f))

    # 2. Read uploaded audio file into memory
    audio_bytes = await audio.read()

    # 3. Transcribe with Whisper
    transcription = openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=(audio.filename, audio_bytes),
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
    cleaned_text = tars_text.replace("**", "").replace("$", "").replace("/", "")
    response = elevenlabs_client.text_to_speech.convert(
        voice_id="dNXy174F4uFM8G0CUjYL",  # TARS-like voice
        output_format="mp3_22050_32",
        text=cleaned_text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.75,
            similarity_boost=0.99,
            style=0.0,
            use_speaker_boost=False,
        ),
    )

    # Save audio file
    run_id = str(uuid.uuid4())[:8]
    audio_path = f"outputs/response_{run_id}.mp3"
    with open(audio_path, "wb") as f:
        f.write(response)

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
