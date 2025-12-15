from typing import Optional, List, Dict, Any
import sys
import os
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.api_core import exceptions
from gen_tts.config import settings, USER_CONFIG_FILE
from gen_tts.utils import wave_file

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
    speaker_voices_map: Optional[List[Dict[str, Any]]] = None,
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

        if not response.candidates:
             raise RuntimeError(f"Gemini API returned no candidates. Full response: {response}")

        candidate = response.candidates[0]
        
        # Check for unsuccessful finish reasons
        if candidate.finish_reason != 1: # 1 is typically STOP/SUCCESS in the proto enum, but looking at the object is safer if we can map it. 
                                         # The library usually exposes an enum. Let's rely on the string representation or just check content existence first.
            # If there's no content, it's definitely an error
            if not candidate.content or not candidate.content.parts:
                 finish_reason_str = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                 safety_ratings = getattr(candidate, 'safety_ratings', 'N/A')
                 raise RuntimeError(f"Gemini API generation failed. Finish Reason: {finish_reason_str}. Safety Ratings: {safety_ratings}. Response: {response}")

        try:
            audio_data = candidate.content.parts[0].inline_data.data
        except (AttributeError, IndexError) as e:
             raise RuntimeError(f"Unexpected response format from Gemini API: {response}") from e

        if not audio_data:
            raise RuntimeError("Gemini API returned empty audio data.")
        
        if audio_format.upper() == "WAV":
            # Gemini typically returns raw PCM (LINEAR16) for audio generation.
            # We must wrap it in a WAV container with the correct header.
            # Defaulting to 24kHz as is common for Gemini TTS.
            wave_file(output_file, audio_data, rate=24000)
        else:
            # For other formats (like MP3 if we were to support it natively via API config),
            # or if we just want to save the raw bytes.
            with open(output_file, "wb") as f:
                f.write(audio_data)

    except exceptions.GoogleAPICallError as e:
        snippet = text[:100] + "..." if len(text) > 100 else text
        raise RuntimeError(f"Error during Gemini speech synthesis for prompt '{snippet}': {e}") from e