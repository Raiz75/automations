---
title: Automations Home
aliases:
  - Project Hub
  - automations
tags:
  - automations
  - home
---

# Automations

A Flask web application that exposes two media-generation engines as a unified web interface — a **Text-to-Speech** engine and a **Quote Video Maker** for social media content.

> [!info] Quick Links
> - [[main-app-flask|Main App (Flask)]] — web layer, routes, API endpoints
> - [[tts-engine|TTS Engine]] — Kokoro ONNX neural speech synthesis
> - [[quote-video-engine|Quote Video Engine]] — video rendering pipeline
> - [[orchestration-layer|Orchestration Layer]] — batch generation, state, asset pairing
> - [[frontend-ui|Frontend & UI]] — templates, JavaScript, CSS
> - [[data-flow-architecture|Data Flow & Architecture]] — end-to-end flow

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Flask (Python) |
| TTS | Kokoro ONNX (`kokoro-onnx`), Soundfile, Pydub |
| Video | MoviePy 1.0.3, Pillow (PIL), NumPy |
| Frontend | Vanilla JS, CSS3 |
| Audio | MP3 @ 192kbps |

## Project Structure

```
automations/
├── .gitignore
├── .obsidian/                    # Vault config & docs
├── docs/superpowers/             # Original design specs & plans
│   ├── plans/
│   └── specs/
├── engine/
│   ├── TTS/                      # Text-to-speech engine
│   │   ├── tts_engine.py         # Kokoro model wrapper
│   │   ├── kokoro-v1.0.onnx     # ONNX model (~310 MB, gitignored)
│   │   ├── voices-v1.0.bin      # Voice pack (gitignored)
│   │   ├── voice-sample/         # Pre-generated preview MP3s (54 files)
│   │   └── output/               # Generated audio
│   └── quote-video-maker/        # Quote video engine
│       ├── __init__.py
│       ├── render_quote.py       # Core rendering (PIL + MoviePy)
│       ├── quote_video_engine.py # Orchestration layer
│       ├── config.json           # Rendering parameters
│       ├── state.json            # Batch counter
│       ├── state.example.json    # Example state file
│       ├── prompts/              # LLM master prompt
│       ├── bg-image/             # Background images
│       ├── bg-music/             # Background music
│       ├── output/               # Generated MP4s
│       └── yt-files/             # YouTube export files
└── main/
    ├── app.py                    # Flask entry point
    ├── routes.py                 # All HTTP routes & API
    ├── requirements.txt
    ├── static/
    │   ├── style.css             # 826 lines of styling
    │   └── js/
    │       └── project_activation.js
    └── templates/
        ├── _base.html            # Base layout (sidebar, content, bot console)
        ├── index.html            # Overview landing page
        ├── tts.html              # TTS interface
        ├── quote-video.html      # Quote video interface
        └── _partials/            # Reusable template fragments
            ├── bot_panel.html
            ├── project_content.html
            └── project_header.html
```

## Port

The app runs on **port 5001** in debug mode.

## Related

- [[data-flow-architecture#System Diagram|System Architecture Diagram]]
