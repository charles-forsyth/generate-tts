import datetime
import os
import platform
import re
import subprocess
import sys
import wave


def create_filename(text: str, audio_format: str) -> str:
    """Generate a safe filename based on the input text and current timestamp."""
    # Sanitize text for filename (remove special characters, replace spaces)
    sanitized_text = re.sub(r'[^a-zA-Z0-9_\-.]', '', text[:50].replace(' ', '_'))

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = audio_format.lower()

    if sanitized_text:
        return f"gemini_tts_{sanitized_text}_{timestamp}.{extension}"
    else:
        return f"gemini_tts_{timestamp}.{extension}"

def play_audio(filename: str) -> None:
    """Play an audio file using a cross-platform method."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(
                ["afplay", filename],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif system == "Linux":  # Linux
            # Prioritize ffplay (from ffmpeg), then play (sox), then paplay, then aplay
            if os.system("which ffplay > /dev/null") == 0:
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", filename],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif os.system("which play > /dev/null") == 0:
                subprocess.run(
                    ["play", filename],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif os.system("which paplay > /dev/null") == 0:
                subprocess.run(
                    ["paplay", filename],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif os.system("which aplay > /dev/null") == 0:
                subprocess.run(
                    ["aplay", filename],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                print(
                    "Warning: No suitable audio player found (ffplay, play, paplay, aplay). "
                    "Please install one to enable audio playback.",
                    file=sys.stderr
                )
        elif system == "Windows":  # Windows
            os.startfile(filename) # type: ignore
        else:
            print(f"Warning: Unsupported OS '{system}' for audio playback.", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Audio player not found. Cannot play '{filename}'.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio file '{filename}': {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during audio playback: {e}", file=sys.stderr)

def wave_file(
    filename: str,
    pcm: bytes,
    channels: int = 1,
    rate: int = 24000,
    sample_width: int = 2
) -> None:
   """Write raw PCM data to a WAV file."""
   # This function is specifically for writing WAV files.
   # If Gemini returns raw PCM, this can be used.
   # For simplicity, if Gemini returns a ready-to-save blob (e.g., MP3 or WAV with headers),
   # it should be saved directly.
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

def convert_audio_format(input_file: str, output_file: str) -> None:
    """Convert audio file format using ffmpeg."""
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_file, "-y", output_file],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Please install ffmpeg to support audio conversion."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Error converting audio to {output_file}. Ensure ffmpeg is installed and working."
        ) from e
