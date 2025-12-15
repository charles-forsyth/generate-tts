# Gen-TTS

Gen-TTS is a powerful command-line interface (CLI) tool that leverages Google Gemini's native Text-to-Speech (TTS) capabilities to convert text into high-quality, natural-sounding audio. It supports both single-speaker and multi-speaker audio generation, offering fine-grained control over voice selection, style, accent, pace, and tone through advanced prompting techniques.

## Features

*   **Single-Speaker TTS**: Generate audio from text using a wide range of prebuilt Gemini voices.
*   **Multi-Speaker TTS**: Create dynamic conversations with up to two distinct speakers, each with their own assigned voice.
*   **Advanced Prompting**: Utilize detailed audio profiles, scene descriptions, and director's notes (via Markdown files) to guide the TTS model's performance for expressive and nuanced output.
*   **Flexible Input**: Provide text directly as an argument, read from a file, or pipe content via standard input.
*   **Multiple Output Formats**: Save generated audio in WAV or MP3 formats.
*   **Temporary Playback**: Quickly preview generated speech without saving a permanent file.
*   **Cross-Platform Audio Playback**: Automatically plays generated audio on macOS, Linux, and Windows.
*   **Configurable**: Easily manage your Google API key and project ID through a `.env` file.

## Installation

1.  **Clone the repository (if applicable)**:

    ```bash
    git clone https://github.com/your-repo/gen-tts.git
    cd gen-tts
    ```

2.  **Create a virtual environment and install dependencies**:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip setuptools
    pip install -e .
    ```

    For development dependencies:
    ```bash
    pip install -e .[dev]
    ```

## Configuration

Gen-TTS requires a Google Cloud API key for authentication with the Gemini API. Upon first run, if the configuration file doesn't exist, it will be created at `~/.config/gen-tts/.env`.

1.  **Locate or Create `.env` file**: The script will guide you to create it if it doesn't exist. Alternatively, you can create it manually:

    ```bash
    mkdir -p ~/.config/gen-tts
    touch ~/.config/gen-tts/.env
    ```

2.  **Add your Google Cloud API Key**: Open `~/.config/gen-tts/.env` and add your API key:

    ```
    # Google Cloud API Key (for Gemini TTS authentication)
    GOOGLE_API_KEY='YOUR_GEMINI_API_KEY'

    # Your Google Cloud Project ID (optional, but good practice)
    GCLOUD_PROJECT='your-google-cloud-project-id'
    ```
    Replace `YOUR_GEMINI_API_KEY` with your actual Google Cloud API Key.

## Usage

### Basic Single-Speaker TTS

```bash
gen-tts "The quick brown fox jumps over the lazy dog." --voice-name Zephyr --temp
```

### Saving to a File

```bash
gen-tts "This is an important announcement." --voice-name Kore --output-file announcement.mp3 --audio-format MP3
```

### Multi-Speaker TTS

For multi-speaker output, your input text should be formatted to indicate speakers (e.g., "SpeakerName: Text").

```bash
gen-tts "Joe: How's it going today Jane?\nJane: Not too bad, how about you?" \
        --multi-speaker \
        --speaker-voices Joe=Kore Jane=Puck \
        --output-file conversation.wav
```

### Using a Detailed Prompt (Audio Profile, Scene, Director's Notes)

Create a Markdown file (e.g., `jaz_prompt.md`) with your detailed prompt:

```markdown
# AUDIO PROFILE: Jaz R.
## "The Morning Hype"

## THE SCENE: The London Studio
It is 10:00 PM in a glass-walled studio overlooking the moonlit London skyline,
but inside, it is blindingly bright. The red "ON AIR" tally light is blazing.
Jaz is standing up, not sitting, bouncing on the balls of their heels to the
rhythm of a thumping backing track. Their hands fly across the faders on a
massive mixing desk. It is a chaotic, caffeine-fueled cockpit designed to wake
up an entire nation.

### DIRECTOR'S NOTES
Style:
* The "Vocal Smile": You must hear the grin in the audio. The soft palate is
always raised to keep the tone bright, sunny, and explicitly inviting.
* Dynamics: High projection without shouting. Punchy consonants and elongated
vowels on excitement words (e.g., "Beauuutiful morning").

Pace: Speaks at an energetic pace, keeping up with the fast music.  Speaks
with A "bouncing" cadence. High-speed delivery with fluid transitions — no dead
air, no gaps.

Accent: Jaz is from Brixton, London

### SAMPLE CONTEXT
Jaz is the industry standard for Top 40 radio, high-octane event promos, or any
script that requires a charismatic Estuary accent and 11/10 infectious energy.

#### TRANSCRIPT
Yes, massive vibes in the studio! You are locked in and it is absolutely
popping off in London right now. If you're stuck on the tube, or just sat
there pretending to work... stop it. Seriously, I see you. Turn this up!
We've got the project roadmap landing in three, two... let's go!
```

Then run:

```bash
gen-tts --detailed-prompt-file jaz_prompt.md --output-file jaz_radio.mp3
```

### Listing Available Voices

```bash
gen-tts --list-voices
```

### Piped Input

```bash
cat my_script.txt | gen-tts --temp --voice-name Puck
```

## Development

### Running Tests

```bash
source .venv/bin/activate
pytest
```

### Linting and Formatting

```bash
source .venv/bin/activate
ruff check .
ruff format .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/your-repo/gen-tts/issues).
