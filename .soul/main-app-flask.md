---
title: Main App (Flask)
aliases:
  - Flask App
  - Web Layer
  - Routes
tags:
  - automations
  - flask
  - backend
---

# Main App (Flask)

The web frontend and API layer. Built with Flask, runs on port 5001.

## Entry Point — `app.py`

Creates the Flask application, injects engine directories into `sys.path`, registers routes, and starts the dev server.

```python
# Key lines (app.py)
sys.path.insert(0, engine_dir)         # engine/quote-video-maker/
sys.path.insert(0, tts_dir)            # engine/TTS/
sys.path.insert(0, parent_dir)         # engine/
app.run(debug=True, port=5001)
```

## Routes — `routes.py`

### Page Routes

| Method | Path | Template | Description |
|---|---|---|---|
| GET | `/` | `index.html` | Overview landing |
| GET | `/tts` | `tts.html` | TTS interface |
| GET | `/quote-video` | `quote-video.html` | Quote video interface |

### General API

| Method | Path | Description |
|---|---|---|
| GET | `/api/navigation` | Sidebar nav items |
| GET | `/api/projects` | Project listing |

### TTS API

| Method | Path | Description |
|---|---|---|
| POST | `/api/tts/generate` | Generate speech from text + voice |
| GET | `/api/tts/audio/<filename>` | Serve MP3 file |
| GET | `/api/tts/voices` | List all 54 voices |
| GET | `/api/tts/status` | Engine health check |
| GET | `/api/tts/preview/<voice>` | Generate & cache voice preview |

> [!tip] Audio files are served from `engine/TTS/output/`

### Quote Video API

| Method | Path | Description |
|---|---|---|
| GET | `/api/quote-video/status` | Engine health + asset counts |
| GET | `/api/quote-video/assets` | List available images & music |
| GET | `/api/quote-video/config` | Return `config.json` |
| GET | `/api/quote-video/master-prompt` | Return master prompt text |
| POST | `/api/quote-video/generate` | Trigger batch video generation |
| GET | `/api/quote-video/output/<filename>` | Serve MP4 file |

> [!warning] Path Redundancy
> Both `app.py` and `routes.py` add engine paths to `sys.path`. This works but is redundant — `routes.py` duplicates the setup for standalone testability.

## Dependencies (`requirements.txt`)

```
flask
kokoro-onnx
soundfile
pydub
moviepy==1.0.3
pillow
numpy
```

## Related

- [[automations-home|Home]]
- [[tts-engine|TTS Engine]]
- [[quote-video-engine|Quote Video Engine]]
- [[frontend-ui|Frontend & UI]]
