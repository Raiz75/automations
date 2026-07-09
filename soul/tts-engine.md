---
title: TTS Engine
aliases:
  - Text-to-Speech
  - Kokoro TTS
tags:
  - automations
  - tts
  - kokoro
  - audio
---

# TTS Engine

Neural text-to-speech using the **Kokoro ONNX** model. Located at `engine/TTS/`.

## Architecture

```
POST /api/tts/generate {text, voice}
    → tts_engine.generate_speech(text, voice)
        → Kokoro ONNX inference (WAV)
        → Pydub transcodes WAV → MP3 @ 192kbps
        → Deletes intermediate WAV
    → Returns /api/tts/audio/<filename>
```

## Core File — `tts_engine.py`

| Function | Description |
|---|---|
| `generate_speech(text, voice)` | Generate audio, save MP3, return filename |
| `get_status()` | Check model & voice files exist |

### Model Files

| File | Size | Gitignored |
|---|---|---|
| `kokoro-v1.0.onnx` | ~hundreds MB | Yes |
| `voices-v1.0.bin` | ~hundreds MB | Yes |

> [!warning] Model files are gitignored — they must be present at runtime or the engine returns unhealthy status.

## Voices (54 total)

8 language variants with codes:

| Prefix | Language | Examples |
|---|---|---|
| `af_` | American English (female) | `af_heart`, `af_alloy`, `af_nicole` |
| `am_` | American English (male) | `am_adam`, `am_michael`, `am_liam` |
| `bf_` | British English (female) | `bf_alice`, `bf_emma`, `bf_lily` |
| `bm_` | British English (male) | `bm_daniel`, `bm_george`, `bm_james` |
| `jf_` | Japanese (female) | `jf_alpha`, `jf_gongitsune` |
| `zm_` | Mandarin (male) | `zm_yunxi`, `zm_yunyang` |
| `ef_` | Spanish (female) | `ef_dora` |
| `ff_` | French (female) | `ff_siwis` |
| `hf_` | Hindi (female) | `hf_alpha` |
| `if_` | Italian (female) | `if_sara` |

## Voice Previews

Pre-generated MP3 samples are cached in `voice-sample/` — one per voice, created on first request via `/api/tts/preview/<voice>`.

## Output

Generated audio files go to `engine/TTS/output/` and are served via [[main-app-flask|Flask]].

## Related

- [[main-app-flask#TTS API|TTS API Routes]]
- [[automations-home|Home]]
