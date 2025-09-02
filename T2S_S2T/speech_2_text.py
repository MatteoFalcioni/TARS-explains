from elevenlabs import play, VoiceSettings
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

from TARS.state import TARSState

load_dotenv()

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=os.getenv("XI_API_KEY"))

def play_audio(state: TARSState):
    
    """Plays the audio response from the remote graph with ElevenLabs."""

    # Response from the agent 
    response = state['messages'][-1]

    # Prepare text by replacing ** with empty strings
    # These can cause unexpected behavior in ElevenLabs
    cleaned_text = response.content.replace("**", "")
    
    # Call text_to_speech API with turbo model for low latency
    response = elevenlabs_client.text_to_speech.convert(
        voice_id="dNXy174F4uFM8G0CUjYL", # Adam pre-made voice
        output_format="mp3_22050_32",
        text=cleaned_text,
        model_id="eleven_turbo_v2_5", 
        voice_settings=VoiceSettings(
            stability=0.8,         # a bit less flat → slight inflection
            similarity_boost=0.95,  # lean into the cloned timbre
            style=0.1,             # tiny expressiveness
            use_speaker_boost=False # avoid cinematic boom
        )
    )
    
    # Play the audio back
    play(response)