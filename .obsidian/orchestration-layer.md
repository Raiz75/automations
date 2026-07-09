---
title: Orchestration Layer
aliases:
  - quote_video_engine
  - Batch Generator
tags:
  - automations
  - orchestration
  - video
  - state
---

# Orchestration Layer

The `quote_video_engine.py` module orchestrates batch video generation — it sits between the [[main-app-flask|Flask API]] and the [[quote-video-engine|video renderer]].

## Functions

| Function | Description |
|---|---|
| `batch_generate(quotes_json)` | Parse JSON, pair with assets, render each quote |
| `get_status()` | Return engine health + asset counts |
| `get_assets()` | List available background images & music |
| `get_config()` | Return config.json contents |
| `get_master_prompt()` | Return master prompt text |

## Batch Generation Flow

```
POST /api/quote-video/generate {quotes: [...]}
    → batch_generate(quotes_json)
        1. Parse JSON array of {text, author}
        2. Scan bg-image/ directory for available images
        3. Scan bg-music/ directory for available tracks
        4. Randomly pair each quote with an image + music
        5. Group into batches (2 quotes per batch)
        6. Increment state.json → get next_batch number
        7. For each quote:
            → render_quote_video(text, author, img, music, output_path, config)
        8. Return results: filenames, status per quote, summary
```

> [!info] Each quote gets a unique filename like `20260709_090732_902_b0002_s1.mp4` — timestamp, batch number, and sequence number.

## Asset Pairing

- **Images:** Randomly selected from `bg-image/` — each quote gets a random image
- **Music:** Randomly selected from `bg-music/` — each quote gets a random track
- Assets are scanned fresh on every generation call

## State — `state.json`

```json
{ "next_batch": 15 }
```

A persistent counter that increments by the number of batches per run. Ensures unique filenames across:

- Server restarts
- Multiple generation sessions
- Concurrent requests (single-threaded per request)

> [!warning] `state.json` is **not** concurrency-safe — two simultaneous requests could read/write the same batch number. The engine processes requests single-file through Flask's default behavior.

## Master Prompt — `prompts/master_prompt.txt`

A detailed LLM prompt for generating viral quotes via AI:

- 30 themes (Life Lessons, Breakup, Self-Growth, etc.)
- 14 quotes per generation, at least 5 must be original
- Rhyme & rhythm requirements
- Hook patterns & cliche replacement rules
- Output format: strict JSON only, no preamble

## Asset Directories

| Directory | Contents | Gitignored? |
|---|---|---|
| `bg-image/` | Background images (e.g. `page16.png`) | Partial (images yes, `.gitkeep` no) |
| `bg-music/` | Background music tracks (e.g. `bgMusic.mp3`) | Partial (music yes, `.gitkeep` no) |
| `output/` | Generated MP4 videos | Partial (videos yes, `.gitkeep` no) |

## Related

- [[quote-video-engine|Quote Video Engine (render_quote.py)]]
- [[main-app-flask#Quote Video API|Quote Video API]]
- [[automations-home|Home]]
