# Gen-TTS: Gemini Native Audio Generation CLI

`gen-tts` is a powerful command-line interface for Google's Gemini Native Text-to-Speech (TTS) capabilities. It allows you to generate high-quality, expressive speech from text, including single-speaker narration, multi-speaker conversations, and AI-generated podcasts and summaries.

Powered by the **Gemini 2.5** and **Gemini 2.0** models.

## Features

-   **High-Quality Voices:** Access Gemini's full range of expressive voices (e.g., Charon, Kore, Fenrir, Puck).
-   **Multi-Speaker Support:** Generate conversations between different speakers with distinct voices.
-   **Podcast Mode:** Automatically turn any text or file into a lively "Deep Dive" podcast conversation between two hosts.
-   **Summary Mode:** Summarize long text into a concise, information-packed audio briefing read by a warm, professional voice.
-   **Transcript Generation:** Ask Gemini to write a script for you based on a topic, then immediately synthesize it.
-   **MP3 Support:** Automatically converts output to MP3 (requires `ffmpeg`) or WAV.
-   **Cross-Platform Playback:** Automatically plays the generated audio on Linux, macOS, and Windows.

## Installation

### Prerequisites
-   **Python 3.9+**
-   **ffmpeg** (Required for MP3 support and playback on Linux)
    -   *Linux:* `sudo apt install ffmpeg`
    -   *macOS:* `brew install ffmpeg`

### Install via uv (Recommended)
```bash
uv tool install git+https://github.com/charles-forsyth/generate-tts.git
```

### Install via pip
```bash
pip install git+https://github.com/charles-forsyth/generate-tts.git
```

## Configuration

The tool requires a Google Cloud API Key. On first run, it will create a config file at `~/.config/gen-tts/.env` where you can paste your key.

```bash
# ~/.config/gen-tts/.env
GOOGLE_API_KEY="your_actual_api_key_here"
```

## Usage

### 1. Basic Single Speaker
Generate audio from text. Default voice is **Charon** (Deep, Warm Male).

```bash
gen-tts "System systems operational." --temp
```
*`--temp` plays the audio immediately without saving a file.*

### 2. Podcast Mode ("Deep Dive")
Turn an article, report, or text into an engaging podcast conversation between two hosts (**Fenrir** and **Leda**).

```bash
# From a file
gen-tts --input-file article.txt --podcast --output-file deep_dive.mp3

# Piping text
echo "Breaking news..." | gen-tts --podcast
```

### 3. Summary Mode
Summarize text into a concise, professional audio briefing. Default voice is **Charon**.

```bash
cat report.txt | gen-tts --summary --output-file briefing.mp3
```

### 4. Topic-Based Generation
Ask Gemini to write a script for you and then speak it.

```bash
gen-tts --generate-transcript "A funny debate about coffee vs tea" \
        --multi-speaker --speaker-voices Alice=Kore Bob=Puck \
        --output-file debate.mp3
```

### 5. Custom Multi-Speaker
Provide your own script formatted as `Speaker: Text`.

**script.txt:**
```text
Joe: Hey Jane, did you see the update?
Jane: Yes, it looks amazing!
```

**Command:**
```bash
gen-tts --input-file script.txt --multi-speaker \
        --speaker-voices Joe=Charon Jane=Puck \
        --audio-format MP3
```

### Options Reference

| Flag | Description |
| :--- | :--- |
| `--podcast` | Generate a multi-speaker podcast script from input. |
| `--summary` | Generate a concise summary script from input. |
| `--generate-transcript "TOPIC"` | Generate a script based on a topic. |
| `--multi-speaker` | Enable multi-speaker mode (requires `--speaker-voices`). |
| `--speaker-voices` | Map speakers to voices (e.g., `Host=Fenrir Guest=Leda`). |
| `--voice-name` | Voice for single-speaker mode (Default: `Charon`). |
| `--audio-format` | `WAV` or `MP3`. Defaults to `MP3` for podcasts/summaries. |
| `--model` | TTS Model (Default: `gemini-2.5-flash-preview-tts`). |
| `--transcript-model` | Model for script generation (Default: `gemini-2.5-pro`). |
| `--list-voices` | List all available Gemini voices. |
| `--no-play` | Disable automatic playback. |

## License
MIT License