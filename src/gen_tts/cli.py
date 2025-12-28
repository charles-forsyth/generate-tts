import argparse
import sys
import tempfile
from typing import Any, Optional

from gen_tts.config import ensure_config_exists, settings
from gen_tts.core import (
    SCRIPT_STYLES,
    generate_speech_gemini,
    generate_styled_script,
    generate_transcript_gemini,
    list_gemini_voices,
)
from gen_tts.utils import create_filename, play_audio

# Removed explicit imports of types components as they are constructed as dicts

def list_voices_table(voice_list: list[str]) -> None:
    """Print the available voices in a formatted table."""
    if not voice_list:
        print("No Gemini TTS voices could be fetched.", file=sys.stderr)
        return

    max_name_len = max(len(v) for v in voice_list) if voice_list else 20

    print("Available Gemini TTS Voices:")
    print(f"{ 'Name':<{max_name_len}}")
    print(f"{ '=' * max_name_len}")

    for voice_name in voice_list:
        print(f"{voice_name:<{max_name_len}}")

def main() -> None:
    """Parse command-line arguments and call the voice generation function."""
    # Ensure config exists and permissions are secure
    ensure_config_exists()

    epilog_examples = """
EXAMPLES:

  1. Quick Single Speaker (Default: Charon, WAV):
     gen-tts "System systems operational." --temp

  2. Generate a Podcast ("Deep Dive" style):
     # Turns text into a lively conversation between two hosts
     gen-tts --input-file article.txt --mode podcast --output-file deep_dive.mp3

  3. Generate a Concise Summary:
     # Summarizes input into a warm, professional reading
     cat report.txt | gen-tts --mode summary --output-file briefing.mp3

  4. Generate a Debate:
     gen-tts --input-file topic.txt --mode debate --temp

  5. Generate Audio from a Topic (AI writes the script):
     gen-tts --generate-transcript "A debate about the future of AI" \\
             --multi-speaker --speaker-voices Optimist=Kore Skeptic=Puck \\
             --audio-format MP3 --output-file debate.mp3

  6. Custom Multi-Speaker Conversation:
     # You provide the script file formatted as 'Speaker: Text'
     gen-tts --input-file script.txt --multi-speaker \\
             --speaker-voices Host=Charon Guest=Kore \\
             --audio-format MP3

CONFIGURATION:
  To authenticate with Google Cloud, set your API key in a .env file:
  $ echo "GOOGLE_API_KEY=AIzaSy...YourAPIKey..." >> .env
  $ echo "GCLOUD_PROJECT=your-google-cloud-project-id" >> .env

For more details, visit: https://github.com/charles-forsyth/generate-tts
"""
    parser = argparse.ArgumentParser(
        description=(
            "Generate high-quality speech from text using Google Gemini's "
            "native Text-to-Speech (TTS) capabilities, including "
            "single and multi-speaker options."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_examples
    )

    # --- Input Arguments ---
    input_group = parser.add_argument_group(
        'Input Options (provide one of text, --input-file, --generate-transcript or piped data)'
    )
    input_group.add_argument(
        "text", nargs="?", type=str, default=None,
        help=(
            "The text to synthesize. Optional if using --input-file, --generate-transcript, "
            "or piping text via stdin."
        )
    )
    input_group.add_argument(
        "--input-file", type=str, metavar="FILE",
        help="Read the text to synthesize from a specific file path."
    )
    input_group.add_argument(
        "--detailed-prompt-file", type=str, metavar="FILE",
        help=(
            "Path to a Markdown file containing a detailed prompt "
            "(Audio Profile, Scene, Director's Notes) for advanced TTS control."
        )
    )

    # --- Generation Arguments ---
    gen_group = parser.add_argument_group('Content Generation Options')
    gen_group.add_argument(
        "--generate-transcript", type=str, metavar="TOPIC",
        help="Generate a script for the TTS based on a topic using Gemini."
    )
    gen_group.add_argument(
        "--mode", type=str, choices=list(SCRIPT_STYLES.keys()),
        help=(
            "Transform input text into a specific style (podcast, summary, "
            "interview, storyteller, news, debate, lecture)."
        )
    )
    gen_group.add_argument(
        "--podcast", action="store_true",
        help="Alias for --mode podcast. Convert input into a multi-speaker podcast."
    )
    gen_group.add_argument(
        "--summary", action="store_true",
        help="Alias for --mode summary. Convert input into a concise summary."
    )
    gen_group.add_argument(
        "--transcript-model", type=str, default="gemini-2.5-pro",
        help="The model to use for generating the transcript/script. Default: 'gemini-2.5-pro'."
    )

    # --- Output Arguments ---
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        "--output-file", type=str, metavar="FILE", default=None,
        help=(
            "Save the generated audio to this file. If omitted, a filename "
            "is automatically generated based on the text and timestamp. "
            "Ignored if --temp is used."
        )
    )
    output_group.add_argument(
        "--audio-format", type=str, default="WAV",
        choices=["WAV", "MP3"],
        help=(
            "The audio file format. 'WAV' (default) is uncompressed linear PCM. "
            "'MP3' is widely compatible."
        )
    )
    output_group.add_argument(
        "--temp", action="store_true",
        help=(
            "Generate the audio to a temporary file, play it immediately, "
            "and then delete it. Useful for quick previews."
        )
    )
    output_group.add_argument(
        "--no-play", action="store_true",
        help=(
            "Disable automatic playback of the generated audio file. "
            "Default behavior is to play after generation."
        )
    )

    # --- Voice Configuration ---
    voice_group = parser.add_argument_group('Voice Configuration')
    voice_group.add_argument(
        "--model", type=str, default="gemini-2.5-flash-preview-tts",
        help=(
            "The Gemini TTS model to use. Default: 'gemini-2.5-flash-preview-tts'. "
            "Other options include 'gemini-2.5-pro-preview-tts'."
        )
    )
    voice_group.add_argument(
        "--list-voices", action="store_true",
        help="List all available Gemini TTS voices and exit."
    )

    # Single speaker options
    voice_group.add_argument(
        "--voice-name", type=str, default="Charon", metavar="NAME",
        help=(
            "The specific Gemini TTS voice name to use for single-speaker mode. "
            "Default: 'Charon'. Use --list-voices to see all available options."
        )
    )

    # Multi-speaker options
    voice_group.add_argument(
        "--multi-speaker", action="store_true",
        help="Enable multi-speaker mode. Requires --speaker-voices."
    )
    voice_group.add_argument(
        "--speaker-voices", nargs='+', metavar="SPEAKER=VOICE_NAME",
        help=(
            "Define speaker names and their corresponding voice names for multi-speaker mode. "
            "Example: 'Joe=Charon Jane=Puck'. Requires --multi-speaker."
        )
    )

    # --- Project Configuration ---
    project_group = parser.add_argument_group('Project Configuration')
    project_group.add_argument(
        "--project-id", type=str, default=settings.gcloud_project, metavar="ID",
        help=(
            "The Google Cloud Project ID to bill for usage. "
            "Defaults to the 'GCLOUD_PROJECT' environment variable "
            "or 'ucr-research-computing'. (Note: API key is also used for auth)"
        )
    )

    args = parser.parse_args()

    # --- Logic ---
    try:
        if args.list_voices:
            try:
                valid_voices = list_gemini_voices()
                list_voices_table(valid_voices)
            except RuntimeError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            return

        text_to_synthesize = ""
        detailed_prompt_content: Optional[str] = None

        # Resolve aliases
        if args.podcast:
            if args.mode and args.mode != "podcast":
                parser.error("Conflicting modes selected: --podcast and --mode")
            args.mode = "podcast"
        if args.summary:
            if args.mode and args.mode != "summary":
                parser.error("Conflicting modes selected: --summary and --mode")
            args.mode = "summary"

        # Conflict checks
        if args.generate_transcript and args.mode:
             parser.error(
                 "Choose only one generation method: "
                 "--generate-transcript or --mode/--podcast/--summary."
             )

        # --- Smart Defaults for Modes ---
        speaker_voices_map: Optional[list[dict[str, Any]]] = None
        speakers_list_for_gen = []

        if args.mode:
            config = SCRIPT_STYLES[args.mode]

            # 1. Default Audio Format (Default to MP3 for generated content)
            if args.audio_format == "WAV":
                print(
                    f"{args.mode.capitalize()} mode: Defaulting audio format to MP3.",
                    file=sys.stderr
                )
                args.audio_format = "MP3"

            # 2. Configure Speakers
            if not args.speaker_voices:
                # Apply defaults from config
                default_voices = config["default_voices"]
                args.speaker_voices = [f"{s}={v}" for s, v in default_voices.items()]

                # Automatically enable multi-speaker if > 1 speaker
                if len(default_voices) > 1:
                    args.multi_speaker = True
                else:
                    # Single speaker mode - ensure voice_name matches
                    args.voice_name = list(default_voices.values())[0]

                print(
                    f"{args.mode.capitalize()} mode: Using default speakers: "
                    f"{', '.join(args.speaker_voices)}",
                    file=sys.stderr
                )

            # Populate speaker list for generation
            if args.multi_speaker:
                for sv in args.speaker_voices:
                     speaker, _ = sv.split('=', 1)
                     speakers_list_for_gen.append(speaker)
            else:
                 speakers_list_for_gen = config["default_speakers"]

        # Input validation logic
        if args.input_file and args.text:
            parser.error("argument --input-file: not allowed with a text argument.")
        if args.input_file and not sys.stdin.isatty():
             parser.error("--input-file: not allowed when piping text via stdin.")

        # Determine speakers for custom/transcript modes (if not set by mode logic)
        if not args.mode:
            if args.multi_speaker:
                if not args.speaker_voices:
                    parser.error("--multi-speaker requires --speaker-voices.")

                for sv_pair in args.speaker_voices:
                    if '=' not in sv_pair:
                        parser.error(
                            f"Invalid --speaker-voices format: {sv_pair}. "
                            "Expected SPEAKER=VOICE_NAME."
                        )
                    speaker, voice_name = sv_pair.split('=', 1)
                    speakers_list_for_gen.append(speaker)
            elif args.speaker_voices:
                parser.error("--speaker-voices can only be used with --multi-speaker.")
            else:
                # Defaults
                speakers_list_for_gen = ["Narrator"]

        # Parse speaker map for TTS engine (common for all paths)
        if args.multi_speaker and args.speaker_voices:
             speaker_voices_map = []
             for sv_pair in args.speaker_voices:
                speaker, voice_name = sv_pair.split('=', 1)
                speaker_voices_map.append({
                    "speaker": speaker,
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice_name,
                        }
                    }
                })

        # Handle Content Generation & Input Reading
        if args.generate_transcript:
            print(
                f"Generating transcript for topic: '{args.generate_transcript}' "
                f"using {args.transcript_model}...",
                file=sys.stderr
            )
            text_to_synthesize = generate_transcript_gemini(
                topic=args.generate_transcript,
                speakers=speakers_list_for_gen,
                model=args.transcript_model
            )
            print("\n--- Generated Transcript ---", file=sys.stderr)
            print(text_to_synthesize, file=sys.stderr)
            print("----------------------------\n", file=sys.stderr)

        else:
            # Read input first (for normal TTS or Mode-based source)
            raw_input_text = ""
            if args.input_file:
                with open(args.input_file) as f:
                    raw_input_text = f.read()
            elif args.text:
                raw_input_text = args.text
            elif not sys.stdin.isatty():
                raw_input_text = sys.stdin.read().strip()

            if not raw_input_text and not args.detailed_prompt_file:
                 parser.error(
                    "No input provided. Please provide text, --input-file, --generate-transcript, "
                    "or pipe text to the script."
                )

            if args.mode:
                print(
                    f"Generating {args.mode} script from input content using "
                    f"{args.transcript_model}...",
                    file=sys.stderr
                )
                text_to_synthesize = generate_styled_script(
                    source_text=raw_input_text,
                    mode=args.mode,
                    speakers=speakers_list_for_gen,
                    model=args.transcript_model
                )
                print(f"\n--- Generated {args.mode.capitalize()} Script ---", file=sys.stderr)
                print(text_to_synthesize, file=sys.stderr)
                print("--------------------------------\n", file=sys.stderr)
            else:
                text_to_synthesize = raw_input_text

        # Detailed prompt handling
        if args.detailed_prompt_file:
            with open(args.detailed_prompt_file) as f:
                detailed_prompt_content = f.read()
            if text_to_synthesize:
                detailed_prompt_content = (
                    detailed_prompt_content + "\n#### TRANSCRIPT\n" + text_to_synthesize
                )
            text_to_synthesize = detailed_prompt_content

        if args.temp and args.no_play:
            parser.error("--temp cannot be used with --no-play.")

        # Multi-speaker prompt validation
        if args.multi_speaker and not args.detailed_prompt_file:
            if not (args.generate_transcript or args.mode):
                speaker_in_text = any(
                    f"{s.get('speaker')}:" in text_to_synthesize for s in speaker_voices_map
                )
                if not speaker_in_text:
                     print(
                         "Warning: In multi-speaker mode without a detailed prompt, ensure "
                         "your text is formatted as 'SpeakerName: Text' for proper "
                         "voice assignment.",
                         file=sys.stderr
                     )

        # Validate voice name for single speaker
        if not args.multi_speaker and not args.list_voices:
            try:
                all_gemini_voices = list_gemini_voices()
            except RuntimeError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

            if args.voice_name not in all_gemini_voices:
                parser.error(
                    f"Invalid voice name: '{args.voice_name}'.\nUse "
                    f"--list-voices to see available options for model {args.model}."
                )

        common_generate_args = {
            "text": text_to_synthesize,
            "model": args.model,
            "audio_format": args.audio_format,
            "project_id": args.project_id,
            "voice_name": args.voice_name if not args.multi_speaker else None,
            "speaker_voices_map": speaker_voices_map,
        }

        if args.temp:
            if args.output_file:
                print("Warning: --output-file is ignored when --temp is used.",
                      file=sys.stderr)

            suffix = f".{args.audio_format.lower()}"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) \
                    as temp_audio_file:
                temp_filename = temp_audio_file.name
                try:
                    generate_speech_gemini(**common_generate_args, output_file=temp_filename)
                    play_audio(temp_filename)
                except RuntimeError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
        else:
            output_filename = (
                args.output_file or
                create_filename(text_to_synthesize, args.audio_format)
            )
            try:
                generate_speech_gemini(**common_generate_args, output_file=output_filename)
                if not args.no_play:
                    play_audio(output_filename)
            except RuntimeError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting.", file=sys.stderr)
        sys.exit(0)
