---
title: Data Flow & Architecture
aliases:
  - Architecture
  - System Flow
  - Architecture Diagram
tags:
  - automations
  - architecture
  - data-flow
---

# Data Flow & Architecture

## System Diagram

```mermaid
graph TB
    Browser[Browser] --> Flask[Flask App :5001]
    
    subgraph Flask["Flask Web Application main/"]
        App[app.py] --> Routes[routes.py]
        Routes --> Pages[Page Routes]
        Routes --> API[API Endpoints]
    end
    
    subgraph TTS["TTS Engine engine/TTS/"]
        TEngine[tts_engine.py]
        Kokoro[Kokoro ONNX Model]
        Voices[voices-v1.0.bin]
        TEngine --> Kokoro
        TEngine --> Voices
    end
    
    subgraph QV["Quote Video Engine engine/quote-video-maker/"]
        Orchestrator[quote_video_engine.py]
        Renderer[render_quote.py]
        Config[config.json]
        State[state.json]
        Images[bg-image/]
        Music[bg-music/]
        Prompt[prompts/master_prompt.txt]
        
        Orchestrator --> Renderer
        Orchestrator --> Config
        Orchestrator --> State
        Orchestrator --> Images
        Orchestrator --> Music
        Orchestrator --> Prompt
    end
    
    subgraph MMC["MP4-MP3 Converter engine/mp4-mp3-converter/"]
        MCEngine[engine.py]
        FreeConvert[FreeConvert API]
        MCEngine --> FreeConvert
    end
    
    API -->|POST /tts/generate| TEngine
    API -->|GET /tts/voices| TEngine
    API -->|GET /tts/status| TEngine
    API -->|GET /tts/preview| TEngine
    
    API -->|POST /quote-video/generate| Orchestrator
    API -->|GET /quote-video/status| Orchestrator
    API -->|GET /quote-video/assets| Orchestrator
    API -->|GET /quote-video/config| Orchestrator
    API -->|GET /quote-video/master-prompt| Orchestrator
    
    API -->|POST /mp4-mp3-converter/convert| MCEngine

Renderer -->|Output MP4| OutputVid[output/]
    TEngine -->|Output MP3| OutputAudio[output/]
    
    Flask -->|Serve files| OutputVid
    Flask -->|Serve files| OutputAudio
    
    Browser -->|GET /audio/<file>| Flask
    Browser -->|GET /output/<file>| Flask
```

## End-to-End Flows

### TTS Generation Flow

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Flask
    participant TTS as tts_engine.py
    participant FS as Disk
    
    User->>Browser: Type text, select voice
    Browser->>Flask: POST /api/tts/generate {text, voice}
    Flask->>TTS: generate_speech(text, voice)
    TTS->>FS: Kokoro inference → temp.wav
    TTS->>FS: Pydub transcode → output.mp3
    TTS->>FS: Delete temp.wav
    TTS-->>Flask: {filename: "output.mp3"}
    Flask-->>Browser: {audio_url: "/api/tts/audio/output.mp3"}
    Browser->>Flask: GET /api/tts/audio/output.mp3
    Flask-->>Browser: MP3 stream
    Browser->>User: Play audio
```

### Quote Video Generation Flow

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Flask
    participant QV as quote_video_engine.py
    participant Render as render_quote.py
    participant FS as Disk
    
    User->>Browser: Paste quotes JSON, click Generate
    Browser->>Flask: POST /api/quote-video/generate {quotes: [...]}
    Flask->>QV: batch_generate(quotes_json)
    
    QV->>FS: Scan bg-image/ for images
    QV->>FS: Scan bg-music/ for tracks
    
    loop For each quote
        QV->>QV: Randomly pair image + music
        QV->>FS: Read state.json → next_batch
        QV->>FS: Increment state.json
        
        QV->>Render: render_quote_video(...)
        Render->>FS: Load background image
        Render->>FS: Load background music
        Render->>Render: Apply dark overlay
        Render->>Render: Wrap text to fit margins
        Render->>Render: Generate typewriter frames
        Render->>Render: Apply Ken Burns zoom
        Render->>Render: Composite text layers
        Render->>FS: Write MP4 to output/
    end
    
    QV-->>Flask: {results: [...], summary: {...}}
    Flask-->>Browser: Results with download URLs
    Browser->>User: Show download links
    User->>Browser: Click download
    Browser->>Flask: GET /api/quote-video/output/<file>
    Flask-->>Browser: MP4 stream
```

## Component Dependency Graph

```mermaid
graph LR
    App[app.py] --> Routes[routes.py]
    Routes --> TTS[tts_engine.py]
    Routes --> QV[quote_video_engine.py]
    QV --> Render[render_quote.py]
    Render --> PIL[Pillow]
    Render --> MP[MoviePy]
    Render --> NP[NumPy]
    TTS --> KOK[Kokoro ONNX]
    TTS --> PD[Pydub]
    TTS --> SF[Soundfile]
```

## File System Layout

```
engine/
├── TTS/
│   ├── tts_engine.py            # ← Core logic
│   ├── kokoro-v1.0.onnx        # ONNX model (~310 MB, gitignored)
│   ├── voices-v1.0.bin         # Voice pack (gitignored)
│   ├── voice-sample/            # Pre-generated preview MP3s (54 files)
│   └── output/                  # Generated MP3s
│
└── quote-video-maker/
    ├── __init__.py              # Package init
    ├── render_quote.py          # ← Video rendering
    ├── quote_video_engine.py    # ← Orchestration
    ├── config.json              # ← Rendering params
    ├── state.json               # ← Batch counter
    ├── state.example.json       # Example state file
    ├── prompts/
    │   └── master_prompt.txt
    ├── bg-image/                # Background images (add yours)
    ├── bg-music/                # Background tracks (add yours)
    ├── output/                  # Generated MP4s
    └── yt-files/                # YouTube export files

main/
├── app.py                      # Flask entry point
├── routes.py                   # All HTTP routes & API
├── requirements.txt
├── static/
│   ├── style.css               # 826 lines of styling
│   └── js/
│       └── project_activation.js
└── templates/
    ├── _base.html              # Base layout (sidebar, content, bot console)
    ├── index.html              # Overview landing page
    ├── tts.html                # TTS interface
    ├── quote-video.html        # Quote video interface
    └── _partials/              # Reusable template fragments
        ├── bot_panel.html
        ├── project_content.html
        └── project_header.html
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **No database** | Everything is file-system based — JSON state, flat file assets, output on disk. Simple, portable, no infra. |
| **Sys.path injection** | Engine dirs added to `sys.path` in both `app.py` and `routes.py` — allows standalone imports. |
| **New Kokoro instance per call** | Avoids model sharing issues between requests, at the cost of reloading the model each time. |
| **Single-threaded rendering** | No concurrency protection on `state.json` — relies on Flask's default single-thread behavior. |
| **Vanilla JS frontend** | No framework dependencies. Keeps the UI layer minimal and zero-build. |
| **Modular templates** | Reusable `_partials/` fragments reduce duplication across pages. |

## Related

- [[mp4-mp3-converter|MP4 to MP3 Converter]]
- [[automations-home|Home]]
- [[main-app-flask|Main App (Flask)]]
- [[tts-engine|TTS Engine]]
- [[quote-video-engine|Quote Video Engine]]
- [[orchestration-layer|Orchestration Layer]]
- [[frontend-ui|Frontend & UI]]
