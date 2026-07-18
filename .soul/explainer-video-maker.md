---
title: Explainer Video Maker
aliases:
  - EVM
  - Explainer Engine
tags:
  - automations
  - video
  - rendering
  - moviepy
  - tts
---

# Explainer Video Maker

Generates 1920×1080 explainer videos with TTS narration, auto-detected images, character pose overlays, and hardcoded subtitles. Located at `engine/explainer-video-maker/`.

## Architecture

```
Web UI → POST /api/explainer-video/render {segments_json, video_title}
    → engine.render_video_stream()
        → render_explainer_video() [render_explainer.py]
            → Kokoro TTS per microsegment
            → Composite background + character pose + subtitles
            → Concatenate clips + audio → MP4
        → Yields NDJSON events (start → done/error)
    → Response streamed to frontend
```

### Rendering Pipeline

1. **Parse segments** — validates JSON, extracts microsegments with intent, text, image number, pose
2. **Build image map** — scans `assets/images/`, extracts leading digits from filenames as slot numbers
3. **Per-microsegment TTS** — Kokoro ONNX generates speech at intent-tuned speed + trailing silence
4. **Frame composition** — background image (fit-to-canvas) + character pose overlay (bottom-right) + subtitles (white with black stroke, bottom-center)
5. **Audio assembly** — all microsegment WAVs concatenated with silence padding → single MP3
6. **Video assembly** — MoviePy concatenates image clips, attaches audio track
7. **Intro prepend** — `assets/video/WonderSketch-intro.mp4` prepended if present
8. **Export** — MP4 at 1920×1080 @ 30fps, libx264 + aac

## Core File — `engine.py`

| Function | Description |
|---|---|
| `get_status()` | Check character poses, intro video, Kokoro model, image count |
| `get_assets()` | List numbered images in `assets/images/` |
| `get_master_prompts()` | Return all 3 master prompt files |
| `render_video_stream(segments_json, video_title)` | Generator yielding NDJSON events |

## Image Auto-Detection

Images in `assets/images/` are detected by leading digits:
- `01_intro.jpg` → slot 1
- `49_desc.jpeg` → slot 49
- `10_scene3.png` → slot 10

The `_parse_image_num()` function extracts all leading digits; the rest of the filename is ignored. Slots are referenced in microsegments via `"image": <number>`.

## Character Poses

5 poses available in `assets/character/`:

| Pose File | Key |
|---|---|
| `asking-charPose.png` | `asking` |
| `authority-charPose.png` | `authority` |
| `emphasis-charPose.png` | `emphasis` |
| `explaining-charPose.png` | `explaining` |
| `pointingLeft-charPose.png` | `pointingLeft` |

## Subtitles

Hardcoded via PIL on each frame:
- White text with 3px black stroke (readable on any background)
- Font size 42, auto-wrapped to fit margins
- Centered at bottom of frame

## Intent-Tuned Parameters

| Intent | Speed | Silence (ms) |
|---|---|---|
| `hook` | 0.88 | 350 |
| `setup` | 1.00 | 200 |
| `escalation` | 1.05 | 180 |
| `conflict` | 0.95 | 250 |
| `reveal` | 0.90 | 300 |
| `resolution` | 1.00 | 200 |
| `payoff` | 0.88 | 350 |

## API Routes

| Method | Path | Description |
|---|---|---|
| GET | `/api/explainer-video/status` | Engine health check |
| GET | `/api/explainer-video/assets` | List available images |
| GET | `/api/explainer-video/master-prompts` | Get prompt text (all 3) |
| POST | `/api/explainer-video/render` | Render video (streaming NDJSON) |
| GET | `/api/explainer-video/output/<filename>` | Serve rendered MP4 |

## Events (NDJSON stream from `/render`)

| Event | Fields |
|---|---|
| `start` | `{type, total}` |
| `done` | `{type, filename, path, logs[]}` |
| `error` | `{type, error, logs[]}` |

## Directories

| Directory | Purpose |
|---|---|
| `assets/images/` | Background images for explainer (user places here) |
| `assets/character/` | Character pose PNGs |
| `assets/video/` | Intro video (`WonderSketch-intro.mp4`) |
| `prompts/` | AI prompts for each stage (`master_prompt1..3.txt`) |
| `output/` | Generated MP4s + `.txt` sidecar files |

## Dependencies

Shared with the hub's TTS engine — Kokoro model files at `engine/TTS/kokoro-v1.0.onnx` and `engine/TTS/voices-v1.0.bin` are referenced by path, not duplicated.

## Related

- [[main-app-flask#Explainer Video API|Flask Routes]]
- [[tts-engine]] — shared Kokoro TTS model
- [[automations-home|Home]]
