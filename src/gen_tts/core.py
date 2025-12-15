from typing import Optional, List, Dict, Any
import sys
import os
import tempfile
from google import genai
from google.genai import types
from gen_tts.config import settings, USER_CONFIG_FILE
from gen_tts.utils import wave_file, convert_audio_format

def list_gemini_voices() -> List[str]:
    """Returns a list of available Gemini TTS voices."""
    return [
        'Zephyr', 'Puck', 'Charon', 'Kore', 'Fenrir', 'Leda', 'Orus', 'Aoede',
        'Callirrhoe', 'Autonoe', 'Enceladus', 'Iapetus', 'Umbriel', 'Algieba',
        'Despina', 'Erinome', 'Algenib', 'Rasalgethi', 'Laomedeia', 'Achernar',
        'Alnilam', 'Schedar', 'Gacrux', 'Pulcherrima', 'Achird', 'Zubenelgenubi',
        'Vindemiatrix', 'Sadachbia', 'Sadaltager', 'Sulafat'
    ]

def generate_transcript_gemini(
    topic: str,
    speakers: List[str],
    model: str = "gemini-2.0-flash"
) -> str:
    """Generates a conversation transcript using Gemini, formatted for TTS."""
    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found. Please set it in .env.")
    
    client = genai.Client(api_key=api_key)

    if not speakers:
        # Default for single speaker or unspecified
        speakers = ["Narrator"]

    speakers_str = ", ".join(speakers)
    
    prompt = (
        f"Write a script for a conversation between {speakers_str} about the following topic:\n"
        f"Topic: {topic}\n\n"
        "Formatting Requirements:\n"
        "1. Strictly follow the format: 'SpeakerName: Text'.\n"
        "2. Do not include any markdown, bolding, scene descriptions, or parenthetical actions (e.g., (laughs)).\n"
        "3. Only output the dialogue lines.\n"
        "4. Ensure the speaker names match exactly as provided.\n"
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT"],
                temperature=0.7, # slightly creative but controlled
            )
        )
        
        if not response.text:
             raise RuntimeError("Gemini transcript generation returned empty text.")
             
        return response.text.strip()

    except Exception as e:
         raise RuntimeError(f"Error generating transcript: {e}") from e

def generate_podcast_script(
    source_text: str,
    speakers: List[str],
    model: str = "gemini-2.0-flash"
) -> str:
    """Generates a podcast script from source text using Gemini."""
    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found. Please set it in .env.")
    
    client = genai.Client(api_key=api_key)

    if not speakers:
        speakers = ["Host", "Guest"]
    
    speakers_str = ", ".join(speakers)

    prompt = (
        f"You are a professional podcast producer. Your task is to turn the following source text into a "
        f"lively, engaging, and insightful podcast conversation between two hosts: {speakers_str}.\n\n"
        "Guidelines:\n"
        "- Summarize the key points but also 'deep dive' into the most interesting or surprising details.\n"
        "- The tone should be conversational, enthusiastic, and natural (like a 'Deep Dive' audio overview).\n"
        "- Use analogies and clear explanations for complex topics.\n"
        "- Maintain a dynamic flow between the speakers.\n"
        "- STRICTLY follow the format: 'SpeakerName: Text'.\n"
        "- Do NOT use markdown, stage directions, or parentheticals (e.g., (laughs)).\n"
        "- Only output the dialogue lines.\n\n"
        "Source Text:\n"
        f"{source_text}\n"
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT"],
                temperature=0.7,
            )
        )
        
        if not response.text:
             raise RuntimeError("Gemini podcast generation returned empty text.")
             
        return response.text.strip()

    except Exception as e:
         raise RuntimeError(f"Error generating podcast script: {e}") from e

def generate_summary_script(
    source_text: str,
    model: str = "gemini-2.0-flash"
) -> str:
    """Generates a concise summary script from source text using Gemini."""
    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found. Please set it in .env.")
    
    client = genai.Client(api_key=api_key)

    prompt = (
        "You are an expert summarizer and voiceover writer. Your task is to condense the following source text "
        "into a concise, information-packed summary suitable for audio delivery.\n\n"
        "Guidelines:\n"
        "- The tone should be warm, professional, and authoritative.\n"
        "- Focus on the most critical information and key takeaways.\n"
        "- Ensure the text flows naturally when read aloud.\n"
        "- Do NOT use markdown, bullet points, or stage directions. Write in clear paragraphs.\n"
        "- The output should be ready for a narrator to read immediately.\n\n"
        "Source Text:\n"
        f"{source_text}\n"
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT"],
                temperature=0.5, # Lower temperature for accuracy and conciseness
            )
        )
        
        if not response.text:
             raise RuntimeError("Gemini summary generation returned empty text.")
             
        return response.text.strip()

    except Exception as e:
         raise RuntimeError(f"Error generating summary script: {e}") from e

def generate_speech_gemini(
    text: str,
    output_file: str,
    model: str,
    audio_format: str,
    project_id: Optional[str] = None,
    voice_name: Optional[str] = None,
    speaker_voices_map: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Generates speech from text using the Google Gen AI SDK (V2)."""
    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found. Please set it in .env.")
    
    # Initialize the V2 Client
    client = genai.Client(api_key=api_key)

    # Build the SpeechConfig
    speech_config = None
    if speaker_voices_map:
        # Map the list of dicts to a list of SpeakerVoiceConfig objects
        # input dict structure: {'speaker': 'Name', 'voice_config': {'prebuilt_voice_config': {'voice_name': 'Name'}}}
        speaker_configs = []
        for sv in speaker_voices_map:
            # We can construct the object directly from the dictionary if the keys match
            # But let's be explicit to be safe.
            voice_name_input = sv['voice_config']['prebuilt_voice_config']['voice_name']
            speaker_name = sv['speaker']
            
            speaker_configs.append(
                types.SpeakerVoiceConfig(
                    speaker=speaker_name,
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name_input
                        )
                    )
                )
            )

        speech_config = types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=speaker_configs
            )
        )
    elif voice_name:
        speech_config = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name,
                )
            )
        )
    else:
        raise ValueError("Either voice_name or speaker_voices_map must be provided.")

    try:
        response = client.models.generate_content(
            model=model,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_config
            )
        )

        # Accessing data in V2 SDK
        if not response.candidates:
             raise RuntimeError(f"Gemini API returned no candidates. Full response: {response}")

        candidate = response.candidates[0]
        
        if not candidate.content or not candidate.content.parts:
             finish_reason = getattr(candidate, 'finish_reason', 'UNKNOWN')
             safety_ratings = getattr(candidate, 'safety_ratings', 'N/A')
             raise RuntimeError(f"Gemini API generation failed. Finish Reason: {finish_reason}. Safety Ratings: {safety_ratings}. Response: {response}")

        try:
            audio_data = candidate.content.parts[0].inline_data.data
        except (AttributeError, IndexError) as e:
             raise RuntimeError(f"Unexpected response format from Gemini API: {response}") from e

        if not audio_data:
            raise RuntimeError("Gemini API returned empty audio data.")
        
        # Always wrap in WAV container first because API returns PCM
        if audio_format.upper() == "MP3":
            # Use a temp file for the WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav_path = temp_wav.name
            
            try:
                wave_file(temp_wav_path, audio_data, rate=24000)
                # Convert to MP3
                convert_audio_format(temp_wav_path, output_file)
            finally:
                if os.path.exists(temp_wav_path):
                    os.remove(temp_wav_path)
        else:
            # WAV default
            wave_file(output_file, audio_data, rate=24000)

    except Exception as e:
        snippet = text[:100] + "..." if len(text) > 100 else text
        raise RuntimeError(f"Error during Gemini speech synthesis for prompt '{snippet}': {e}") from e