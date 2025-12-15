import datetime
import os
import platform
import subprocess
import re
import sys

def create_filename(text: str, audio_format: str) -> str:
    """Generates a safe filename based on the input text and current timestamp."""
    # Sanitize text for filename (remove special characters, replace spaces)
    sanitized_text = re.sub(r'[^a-zA-Z0-9_\-.]', '', text[:50].replace(' ', '_'))
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = audio_format.lower()
    
    if sanitized_text:
        return f"gemini_tts_{sanitized_text}_{timestamp}.{extension}"
    else:
        return f"gemini_tts_{timestamp}.{extension}"

def play_audio(filename: str) -> None:
    """Plays an audio file using a cross-platform method."""
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", filename], check=True)
        elif system == "Linux":  # Linux
            # Prioritize play from sox, then paplay, then aplay
            if os.system("which play > /dev/null") == 0:
                subprocess.run(["play", filename], check=True)
            elif os.system("which paplay > /dev/null") == 0:
                subprocess.run(["paplay", filename], check=True)
            elif os.system("which aplay > /dev/null") == 0:
                subprocess.run(["aplay", filename], check=True)
            else:
                print(
                    "Warning: No suitable audio player found (play, paplay, aplay). "
                    "Please install one to enable audio playback.",
                    file=sys.stderr
                )
        elif system == "Windows":  # Windows
            os.startfile(filename) # This opens with the default associated application
        else:
            print(f"Warning: Unsupported OS '{system}' for audio playback.", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Audio player not found. Cannot play '{filename}'.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio file '{filename}': {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during audio playback: {e}", file=sys.stderr)

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   """Helper function to write raw PCM data to a WAV file."""
   # This function is specifically for writing WAV files. 
   # If Gemini returns raw PCM, this can be used.
   # For simplicity, if Gemini returns a ready-to-save blob (e.g., MP3 or WAV with headers),
   # it should be saved directly.
   import wave
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)
