# gen-tts specification

Version 0.2.2 (2026-10-20; code 0.2.2). Owner: Chuck Forsyth.
Repository: `charles-forsyth/generate-tts` (local checkout `~/Projects/Gen-TTS-IVXX`). License: MIT.

## 1. Purpose and scope

`gen-tts` is a Python CLI for generating both **single-speaker narration** and **multi-speaker conversational audio** (podcasts, interviews, debates, summaries, lectures, storytelling) using Google's Gemini Native Text-to-Speech API (`gemini-3.8-flash-tts` default) and Gemini text models (`gemini-3.1-pro-preview` default) for automated script generation and style transformation.

Mirage (`~/Projects/mirage`) shells out to `gen-tts` for all voice synthesis across its `hybrid`, `weather`, `research`, `news-short`, and `deep-news` pipelines.

## 2. Design decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Dedicated per-tool config `~/.config/gen-tts/.env` (`0600`) | Prevents credential collision with other tools. `ensure_config_exists()` creates the file and enforces `0600` permissions on every run. |
| D2 | Multi-speaker turns passed as `types.Part(text=..., speech_metadata=types.SpeechMetadata(speaker=...))` | Gemini 3.8 multi-speaker TTS rejects untagged text parts or legacy inline prefixes with `400 INVALID_ARGUMENT`. `_multi_speaker_contents()` parses `Speaker: line` scripts into structured `Part` objects with `speech_metadata.speaker`. |
| D3 | Two-stage pipeline for `--mode` and `--generate-transcript` | Stage 1 uses `gemini-3.1-pro-preview` (`--transcript-model`) with mode-specific producer prompts (`SCRIPT_STYLES`) to write or transform a script; Stage 2 synthesizes the resulting script with `gemini-3.8-flash-tts` (`--model`). |
| D4 | Automatic audio format default by mode | Direct text synthesis defaults to uncompressed `WAV` (24 kHz 16-bit mono PCM) for lossless downstream editing (e.g. Mirage `ffmpeg` mixing); generative modes (`--mode`, `--podcast`, `--summary`, `--generate-transcript`) default to `MP3`. |
| D5 | Do not combine `--detailed-prompt-file` with per-line narration in orchestrators | Passing a detailed prompt file prepends the prompt to the text payload (`f"{detailed_prompt}\n\n{text}"`), which can cause the TTS model to read lines twice when used on short single-sentence clips. Orchestrators pin `--voice-name` instead. |

## 3. Architecture

```text
gen-tts CLI (src/gen_tts/cli.py)
  |-- ensure_config_exists() & Settings (src/gen_tts/config.py)
  |     `-- ~/.config/gen-tts/.env (GOOGLE_API_KEY, GCLOUD_PROJECT)
  |-- Input resolution (cli.py)
  |     |-- positional text | --input-file | stdin | --generate-transcript TOPIC
  |-- Optional Stage 1: Script generation / transformation (src/gen_tts/core.py)
  |     |-- generate_transcript(topic, model=gemini-3.1-pro-preview, speakers=...)
  |     `-- transform_text_to_script(text, mode, model=gemini-3.1-pro-preview, speakers=...)
  |-- Stage 2: Speech synthesis (core.py -> generate_speech())
  |     |-- Single-speaker: VoiceConfig(prebuilt_voice_config=PrebuiltVoiceConfig(voice_name=...))
  |     |-- Multi-speaker: MultiSpeakerVoiceConfig(speaker_voice_configs=[...])
  |     |     `-- _multi_speaker_contents(text, speaker_voices) -> types.Content(parts=[Part(text, speech_metadata)])
  |     |-- wave_file() writes 24 kHz 16-bit mono WAV (src/gen_tts/utils.py)
  |     `-- convert_audio_format() converts WAV -> MP3 via pydub/ffmpeg when audio_format == "MP3"
  `-- Playback (src/gen_tts/utils.py -> play_audio())
        `-- macOS: afplay | Linux: ffplay / aplay | Windows: startfile
```

### Module map

| File | Responsibility |
|---|---|
| `src/gen_tts/cli.py` | Argument parsing, mode alias expansion (`--podcast`, `--summary`), speaker map parsing (`Speaker=Voice`), default output filename generation, orchestration of script generation + TTS + playback. |
| `src/gen_tts/config.py` | `USER_CONFIG_FILE` (`~/.config/gen-tts/.env`), permission hardening (`0600`), `Settings` (`google_api_key`, `gcloud_project`). |
| `src/gen_tts/core.py` | `list_gemini_voices()` (30 voices), `SCRIPT_STYLES` templates (`podcast`, `summary`, `interview`, `storyteller`, `news`, `debate`, `lecture`), `generate_transcript()`, `transform_text_to_script()`, `_multi_speaker_contents()`, `generate_speech()`. |
| `src/gen_tts/utils.py` | `wave_file()`, `convert_audio_format()`, `create_filename()`, `play_audio()`. |

## 4. Script styles and voice defaults (`SCRIPT_STYLES`)

| Mode | Speakers | Default voice mapping | Producer persona |
|---|---|---|---|
| `podcast` (`--podcast`) | `Host`, `Guest` | `Host=Charon`, `Guest=Kore` | Deep-dive conversational podcast between two hosts (`SpeakerName: Text`). |
| `summary` (`--summary`) | `Narrator` | `Narrator=Charon` | Warm, authoritative executive audio briefing in clean paragraphs. |
| `interview` | `Interviewer`, `Expert` | `Interviewer=Kore`, `Expert=Fenrir` | Structured Q&A probing domain insights. |
| `storyteller` | `Narrator` | `Narrator=Aoede` | Expressive narrative storytelling with pacing and sensory detail. |
| `news` | `Anchor` | `Anchor=Orus` | Crisp, objective broadcast news report. |
| `debate` | `Proponent`, `Opponent` | `Proponent=Puck`, `Opponent=Fenrir` | Point-counterpoint debate formatted as `SpeakerName: Text`. |
| `lecture` | `Professor` | `Professor=Charon` | Clear pedagogical lecture with examples and structured takeaways. |

## 5. Multi-speaker wire format (`_multi_speaker_contents`)

When `multi_speaker=True` and `speaker_voices={"Host": "Charon", "Guest": "Kore"}`:
1. Input text is scanned line-by-line against `^([A-Za-z0-9_\s]+):\s*(.+)$`.
2. Each matching line whose speaker prefix is in `speaker_voices` becomes a `types.Part(text=spoken_text, speech_metadata=types.SpeechMetadata(speaker=speaker_name))`.
3. Non-matching continuation lines are appended to the preceding part's text, or assigned to the first configured speaker if no prefix has appeared yet.
4. If the entire input has no speaker prefixes, a single `types.Part` is emitted assigned to the first speaker in `speaker_voices`.

## 6. Configuration

Stored in `~/.config/gen-tts/.env` (mode `0600`):

```env
GOOGLE_API_KEY=AIza...
GCLOUD_PROJECT=ucr-research-computing
```

- `GOOGLE_API_KEY`: Gemini API key restricted to `generativelanguage.googleapis.com`.
- `GCLOUD_PROJECT`: Project identifier (default `ucr-research-computing`).

## 7. CLI interface

```text
gen-tts [text]
        [--input-file FILE]
        [--detailed-prompt-file FILE]
        [--generate-transcript TOPIC]
        [--mode {podcast,summary,interview,storyteller,news,debate,lecture}]
        [--podcast]
        [--summary]
        [--transcript-model MODEL]          # default: gemini-3.1-pro-preview
        [--output-file FILE]
        [--script-txt-out FILE]
        [--audio-format {WAV,MP3}]          # default: WAV (direct) or MP3 (generative modes)
        [--temp]
        [--no-play]
        [--model MODEL]                     # default: gemini-3.8-flash-tts
        [--list-voices]
        [--voice-name NAME]                 # default: Charon
        [--multi-speaker]
        [--speaker-voices SPEAKER=VOICE ...]
        [--project-id ID]
```

## 8. Requirements traceability

| ID | Requirement | Verified by |
|---|---|---|
| REQ-CLI-1 | `--list-voices` prints all 30 Gemini TTS voices and exits 0. | `tests/test_cli.py::test_list_voices` |
| REQ-CLI-2 | Missing input when stdin is a TTY exits with non-zero status and usage message. | `tests/test_cli.py::test_no_input_error` |
| REQ-CLI-3 | `--input-file` takes precedence even when stdin is non-TTY (e.g. invoked inside subprocesses/background jobs). | `tests/test_cli.py::test_input_file_with_non_tty_stdin` |
| REQ-MULTI-1 | Multi-speaker synthesis builds `MultiSpeakerVoiceConfig` and writes valid audio output. | `tests/test_multi_speaker.py::test_multi_speaker` |
| REQ-MULTI-2 | Each `Speaker: text` turn is tagged with `speech_metadata.speaker` in `Content.parts`. | `tests/test_speaker_parts.py::test_multi_speaker_parts_tagged` |
| REQ-MULTI-3 | Unprefixed lines in multi-speaker mode fall back to the first configured speaker instead of failing. | `tests/test_speaker_parts.py::test_multi_speaker_no_prefix_falls_back_to_first` |

## 9. Known gaps and backlog

- **K1 (Confirmed):** `generate_speech()` performs a single Gemini TTS API call without chunking; very long scripts (>600 words) can hit Gemini TTS's ~3-minute single-call truncation limit. Splitting long single-speaker or multi-speaker scripts into turn batches and concatenating the PCM frames would eliminate truncation on long podcasts.
- **K2 (Confirmed):** `convert_audio_format()` uses `pydub.AudioSegment`, which emits a deprecation warning on Python 3.12 (`audioop` removal in Python 3.13+); replacing `pydub` with direct `ffmpeg` subprocess calls (matching `generate-gemini-voice`) will remove the `audioop` dependency.
