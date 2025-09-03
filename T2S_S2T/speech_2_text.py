from elevenlabs import play, VoiceSettings
from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv
import re  

from TARS.state import TARSState

load_dotenv()

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=os.getenv("XI_API_KEY"))

def add_tars_pauses(text):
    """
    Adds SSML break tags for pauses after sentence-ending punctuation (. and ?).
    This creates TARS's characteristic deliberate pacing.
    Returns the text wrapped in <speak> tags.
    """
    # Use regex to find all periods and question marks, and add a break tag after them.
    # substitute "..." with a long break tag
    text = re.sub(r'\.{3}', '<break time="0.6s"/>', text)
    # The (?!\d) is a "negative lookahead" to avoid matching decimals like "90.5"
    text = re.sub(r'([.?:;!])(?!\d)\s*', r'\1<break time="0.4s"/> ', text)
    # add short pauses as well
    text_with_pauses = re.sub(r'([—])(?!\d)\s*', r'\1<break time="0.1s"/> ', text)
    # Add pauses after "Cooper"
    text = re.sub(r'(Cooper)([,.!?]?)\s*', r'\1\2<break time="0.4s"/> ', text)
    
    # WRAP THE FINAL TEXT IN <speak> TAGS
    # This is what tells ElevenLabs to parse the content as SSML.
    ssml_text = f"<speak>{text_with_pauses}</speak>"
    return ssml_text

def play_audio(state: TARSState):
    
    """Plays the audio response from the remote graph with ElevenLabs."""

    # Response from the agent 
    response = state['messages'][-1]

    # Prepare text by replacing ** with empty strings
    # These can cause unexpected behavior in ElevenLabs
    cleaned_text = response.content.replace("**", "").replace("$", "").replace("/", "" )

    # add pauses
    text_with_ssml = add_tars_pauses(cleaned_text)
    
    # Call text_to_speech API with turbo model for low latency
    response = elevenlabs_client.text_to_speech.convert(
        voice_id="dNXy174F4uFM8G0CUjYL", # Adam pre-made voice
        output_format="mp3_22050_32",
        text=text_with_ssml,
        model_id="eleven_turbo_v2_5", 
        voice_settings=VoiceSettings(
            stability=0.75,         # controls inflection: high value -> robotic
            similarity_boost=0.99,  # lean into the cloned timbre
            style=0.0,             # no expressiveness (slows down latency)
            use_speaker_boost=False # avoid cinematic boom
        )
    )
    
    # Play the audio back
    play(response)



