import os
import tempfile
from typing import Any, Optional

from google import genai
from google.genai import types

from gen_tts.config import settings
from gen_tts.utils import convert_audio_format, wave_file


def list_gemini_voices() -> list[str]:
    """Return a list of available Gemini TTS voices."""
    return [
        'Zephyr', 'Puck', 'Charon', 'Kore', 'Fenrir', 'Leda', 'Orus', 'Aoede',
        'Callirrhoe', 'Autonoe', 'Enceladus', 'Iapetus', 'Umbriel', 'Algieba',
        'Despina', 'Erinome', 'Algenib', 'Rasalgethi', 'Laomedeia', 'Achernar',
        'Alnilam', 'Schedar', 'Gacrux', 'Pulcherrima', 'Achird', 'Zubenelgenubi',
        'Vindemiatrix', 'Sadachbia', 'Sadaltager', 'Sulafat'
    ]

# Configuration for different script generation modes
SCRIPT_STYLES = {
    "podcast": {
        "default_speakers": ["Host", "Guest"],
        "default_voices": {"Host": "Charon", "Guest": "Kore"},
        "prompt_template": (
            "You are a professional podcast producer. Turn the source text into a lively, "
            "engaging 'Deep Dive' podcast conversation.\n"
            "Speakers: {speakers_str}\n"
            "Guidelines:\n"
            "- Summarize key points but deep dive into interesting details.\n"
            "- Tone: Conversational, enthusiastic, natural.\n"
            "- Use analogies for complex topics.\n"
            "- STRICTLY follow format: 'SpeakerName: Text'.\n"
            "- No markdown, stage directions, or parentheticals."
        )
    },
    "summary": {
        "default_speakers": ["Narrator"],
        "default_voices": {"Narrator": "Charon"},
        "prompt_template": (
            "You are an expert summarizer. Condense the source text into a concise, "
            "information-packed audio briefing.\n"
            "Guidelines:\n"
            "- Tone: Warm, professional, authoritative.\n"
            "- Focus on critical info and takeaways.\n"
            "- Write in clear paragraphs for natural reading.\n"
            "- No markdown or bullet points."
        )
    },
    "interview": {
        "default_speakers": ["Interviewer", "Expert"],
        "default_voices": {"Interviewer": "Kore", "Expert": "Fenrir"},
        "prompt_template": (
            "Turn the source text into a radio-style interview.\n"
            "Speakers: {speakers_str}\n"
            "Guidelines:\n"
            "- 'Interviewer' asks insightful questions based on the text.\n"
            "- 'Expert' answers thoroughly using facts from the text.\n"
            "- Tone: Professional, investigative, educational.\n"
            "- STRICTLY follow format: 'SpeakerName: Text'."
        )
    },
    "storyteller": {
        "default_speakers": ["Narrator"],
        "default_voices": {"Narrator": "Puck"},
        "prompt_template": (
            "Rewrite the source text as a compelling story or narrative.\n"
            "Guidelines:\n"
            "- Tone: Captivating, dramatic, storytelling style.\n"
            "- Use vivid imagery and narrative flow.\n"
            "- If dialogue exists in text, incorporate it naturally.\n"
            "- No markdown or stage directions."
        )
    },
    "news": {
        "default_speakers": ["Anchor", "Reporter"],
        "default_voices": {"Anchor": "Charon", "Reporter": "Leda"},
        "prompt_template": (
            "Present the source text as a breaking news segment.\n"
            "Speakers: {speakers_str}\n"
            "Guidelines:\n"
            "- 'Anchor' introduces the story in a studio setting.\n"
            "- 'Reporter' provides details 'from the field'.\n"
            "- Tone: Urgent, professional, broadcast journalism style.\n"
            "- STRICTLY follow format: 'SpeakerName: Text'."
        )
    },
    "debate": {
        "default_speakers": ["Proponent", "Skeptic"],
        "default_voices": {"Proponent": "Orus", "Skeptic": "Aoede"},
        "prompt_template": (
            "Turn the source text into a debate or point-counterpoint discussion.\n"
            "Speakers: {speakers_str}\n"
            "Guidelines:\n"
            "- 'Proponent' argues for the main ideas in the text.\n"
            "- 'Skeptic' questions them or highlights challenges/nuances found in the text.\n"
            "- Tone: Intellectual, spirited, but respectful.\n"
            "- STRICTLY follow format: 'SpeakerName: Text'."
        )
    },
    "lecture": {
        "default_speakers": ["Professor"],
        "default_voices": {"Professor": "Fenrir"},
        "prompt_template": (
            "Present the source text as a structured university lecture.\n"
            "Guidelines:\n"
            "- Tone: Academic, clear, educational.\n"
            "- Use rhetorical questions and structure (Introduction, Core Concepts, Conclusion).\n"
            "- Address the audience as students.\n"
            "- No markdown."
        )
    }
}

def generate_transcript_gemini(
    topic: str,
    speakers: list[str],
    model: str = "gemini-2.0-flash"
) -> str:
    """Generate a conversation transcript using Gemini, formatted for TTS."""
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
        "2. Do not include any markdown, bolding, scene descriptions, "
        "or parenthetical actions (e.g., (laughs)).\n"
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

def generate_styled_script(
    source_text: str,
    mode: str,
    speakers: Optional[list[str]] = None,
    model: str = "gemini-2.0-flash"
) -> str:
    """Generate a script from source text using a specific style mode."""
    if mode not in SCRIPT_STYLES:
        raise ValueError(f"Unknown mode: {mode}. Available: {list(SCRIPT_STYLES.keys())}")

    config = SCRIPT_STYLES[mode]

    # Use provided speakers or defaults from config
    final_speakers = speakers if speakers else config["default_speakers"]
    speakers_str = ", ".join(final_speakers)

    # Format the prompt
    system_instruction = config["prompt_template"].format(speakers_str=speakers_str)
    full_prompt = (
        f"{system_instruction}\n\n"
        "Source Text:\n"
        f"{source_text}\n"
    )

    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found. Please set it in .env.")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT"],
                temperature=0.7,
            )
        )

        if not response.text:
             raise RuntimeError(f"Gemini {mode} generation returned empty text.")

        return response.text.strip()

    except Exception as e:
         raise RuntimeError(f"Error generating {mode} script: {e}") from e

def generate_podcast_script(
    source_text: str,
    speakers: list[str],
    model: str = "gemini-2.0-flash"
) -> str:
    """Wrap generate_styled_script for backward compatibility."""
    return generate_styled_script(source_text, "podcast", speakers, model)

def generate_summary_script(
    source_text: str,
    model: str = "gemini-2.0-flash"
) -> str:
    """Wrap generate_styled_script for backward compatibility."""
    return generate_styled_script(source_text, "summary", ["Narrator"], model)

def generate_speech_gemini(
    text: str,
    output_file: str,
    model: str,
    audio_format: str,
    project_id: Optional[str] = None,
    voice_name: Optional[str] = None,
    speaker_voices_map: Optional[list[dict[str, Any]]] = None,
) -> None:
    """Generate speech from text using the Google Gen AI SDK (V2)."""
    api_key = settings.google_api_key
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found. Please set it in .env.")

    # Initialize the V2 Client
    client = genai.Client(api_key=api_key)

    # Build the SpeechConfig
    speech_config = None
    if speaker_voices_map:
        # Map the list of dicts to a list of SpeakerVoiceConfig objects
        # input dict structure:
        # {'speaker': 'Name', 'voice_config': {'prebuilt_voice_config': {'voice_name': 'Name'}}}
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
             raise RuntimeError(
                 f"Gemini API generation failed. Finish Reason: {finish_reason}. "
                 f"Safety Ratings: {safety_ratings}. Response: {response}"
             )

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
        raise RuntimeError(
            f"Error during Gemini speech synthesis for prompt '{snippet}': {e}"
        ) from e
