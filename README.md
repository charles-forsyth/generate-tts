# Gen-TTS: Gemini Native Audio Generation CLI

`gen-tts` is a command-line interface for Google's Gemini Native Text-to-Speech (TTS) capabilities (`gemini-3.8-flash-tts` default). It generates single-speaker narration, multi-speaker conversations, and AI-written podcasts, debates, interviews, and summaries.

See [SPEC.md](SPEC.md) for the full system specification, multi-speaker wire format, architecture, and requirement traceability.

## Features

- **Gemini 3.8 Native TTS:** Access all 30 expressive voices (`Charon`, `Kore`, `Fenrir`, `Puck`, `Aoede`, `Zephyr`, etc.) on `gemini-3.8-flash-tts` (default) or `gemini-3.8-flash-lite-tts`.
- **Multi-Speaker Conversations:** Synthesize scripts formatted as `Speaker: Text` using `speech_metadata.speaker` part tagging and custom `--speaker-voices` mappings.
- **7 Built-in Producer Modes (`--mode`):** Automatically transform source text or topics into a `podcast` (`--podcast`), `summary` (`--summary`), `interview`, `storyteller`, `news`, `debate`, or `lecture` using `gemini-3.1-pro-preview`.
- **Transcript Generation (`--generate-transcript`):** Have Gemini write a script on a topic and synthesize it in one command, optionally saving the text via `--script-txt-out`.
- **WAV & MP3 Output:** Lossless 24 kHz 16-bit mono PCM `WAV` (default for direct text) or `MP3` (default for generative modes; requires `ffmpeg`).
- **Cross-Platform Playback:** Plays automatically via `afplay` (macOS), `ffplay`/`aplay` (Linux), or `os.startfile` (Windows), or saves silently with `--no-play`.

## Installation

### Prerequisites
- **Python 3.9+** (Python 3.12 recommended)
- **ffmpeg** (Required for MP3 encoding)
  - *macOS:* `brew install ffmpeg`
  - *Linux:* `sudo apt install ffmpeg`

### Install via uv (Recommended)
```bash
uv tool install --python 3.12 git+https://github.com/charles-forsyth/generate-tts.git
```

## Configuration

On first run, `gen-tts` creates `~/.config/gen-tts/.env` with `0600` (owner-only) permissions. Set your Gemini API key (restricted to `generativelanguage.googleapis.com`):

```env
GOOGLE_API_KEY=your_api_key_here
GCLOUD_PROJECT=your_project_id
```

## Usage

### 1. Basic Single Speaker
Default voice is **Charon**.

```bash
gen-tts "All workstation systems operational." --temp
```
*`--temp` plays the audio immediately and deletes the temporary file.*

### 2. Podcast Mode ("Deep Dive")
Turn an article, report, or piped text into a conversation between two hosts (**Charon** and **Kore**):

```bash
gen-tts --input-file article.txt --podcast --output-file deep_dive.mp3
echo "Breaking research update..." | gen-tts --podcast
```

### 3. Summary Mode
Summarize a long document into a concise audio briefing:

```bash
cat report.txt | gen-tts --summary --output-file briefing.mp3
```

### 4. Topic-Based Generation
Ask Gemini to write a script from a topic and speak it:

```bash
gen-tts --generate-transcript "A debate about local vs cloud inference" \
        --multi-speaker --speaker-voices Optimist=Kore Skeptic=Puck \
        --audio-format MP3 --output-file debate.mp3
```

### 5. Custom Multi-Speaker Script
Provide your own script formatted as `Speaker: Text`:

```text
Host: Welcome back. Did the migration finish?
Guest: Every tool is online and verified.
```

```bash
gen-tts --input-file script.txt --multi-speaker \
        --speaker-voices Host=Charon Guest=Kore \
        --audio-format WAV --output-file conversation.wav --no-play
```

## Options Reference

| Flag | Description |
| :--- | :--- |
| `text` | Positional text to synthesize. |
| `--input-file FILE` | Read input text from a file. |
| `--detailed-prompt-file FILE` | Markdown file with Audio Profile / Director's Notes for single-speaker styling. |
| `--generate-transcript TOPIC` | Generate a script from a topic using Gemini before synthesizing. |
| `--mode {podcast,summary,interview,storyteller,news,debate,lecture}` | Transform input text into the specified style. |
| `--podcast` | Alias for `--mode podcast`. |
| `--summary` | Alias for `--mode summary`. |
| `--transcript-model MODEL` | Model for script generation/transformation (default: `gemini-3.1-pro-preview`). |
| `--output-file FILE` | Save generated audio to this path. |
| `--script-txt-out FILE` | Save the generated/transformed transcript text to a file. |
| `--audio-format {WAV,MP3}` | Output format (`WAV` default for direct text, `MP3` default for generative modes). |
| `--temp` | Play from a temporary file and delete it afterward. |
| `--no-play` | Do not play audio after synthesis. |
| `--model MODEL` | TTS model (default: `gemini-3.8-flash-tts`; also `gemini-3.8-flash-lite-tts`). |
| `--voice-name NAME` | Voice for single-speaker mode (default: `Charon`). |
| `--multi-speaker` | Enable multi-speaker synthesis (requires `--speaker-voices`). |
| `--speaker-voices SPEAKER=VOICE ...` | Speaker-to-voice map (e.g. `Host=Charon Guest=Kore`). |
| `--list-voices` | List all 30 available Gemini TTS voices and exit. |

## Development

```bash
uv sync --python 3.12
uv run --python 3.12 pytest
```

## License
MIT License
