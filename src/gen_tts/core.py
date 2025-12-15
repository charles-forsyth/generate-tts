from typing import Optional, List, Dict, Any
import sys
import os
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.api_core import exceptions
from gen_tts.config import settings, USER_CONFIG_FILE

def list_gemini_voices() -> List[str]:
    """Returns a list of available Gemini TTS voices."""
    # This function is a placeholder as Gemini API currently does not expose
    # a direct way to list prebuilt voice names via a client method.
    # The voices are hardcoded based on the documentation provided.
    # In a real scenario, if an API to list them existed, it would be used here.
    return [
        'Zephyr', 'Puck', 'Charon', 'Kore', 'Fenrir', 'Leda', 'Orus', 'Aoede',
        'Callirrhoe', 'Autonoe', 'Enceladus', 'Iapetus', 'Umbriel', 'Algieba',
        'Despina', 'Erinome', 'Algenib', 'Rasalgethi', 'Laomedeia', 'Achernar',
        'Alnilam', 'Schedar', 'Gacrux', 'Pulcherrima', 'Achird', 'Zubenelgenubi',
        'Vindemiatrix', 'Sadachbia', 'Sadaltager', 'Sulafat'
    ]

def generate_speech_gemini(
    text: str,
    output_file: str,
    model: str,
    audio_format: str,
    project_id: Optional[str] = None,
    voice_name: Optional[str] = None,
    speaker_voices_map: Optional[List[Dict[str, Any]]] = None, # Change type hint to Dict[str, Any]
) -> None:
    """Generates speech from text using Google Gemini's native Text-to-Speech (TTS) capabilities."""
    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found. Please set it in .env.")
    genai.configure(api_key=api_key)

    gemini_model = GenerativeModel(model)

    # Manually construct the generation_config dictionary
    generation_config: Dict[str, Any] = {
        "response_modalities": ["AUDIO"],
        "speech_config": {}
    }

    if speaker_voices_map:
        # speaker_voices_map is already a list of dicts from cli.py
        generation_config["speech_config"]["multi_speaker_voice_config"] = {
            "speaker_voice_configs": speaker_voices_map
        }
    elif voice_name:
        generation_config["speech_config"]["voice_config"] = {
            "prebuilt_voice_config": {
                "voice_name": voice_name,
            }
        }
    else:
        raise ValueError("Either voice_name or speaker_voices_map must be provided.")

    try:
        response = gemini_model.generate_content(
            contents=text,
            generation_config=generation_config
        )

        audio_data = response.candidates[0].content.parts[0].inline_data.data
        
        with open(output_file, "wb") as f:
            f.write(audio_data)

    except exceptions.GoogleAPICallError as e:
        snippet = text[:100] + "..." if len(text) > 100 else text
        raise RuntimeError(f"Error during Gemini speech synthesis for prompt '{snippet}': {e}") from e