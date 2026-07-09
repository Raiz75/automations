---
title: Quote Video Engine
aliases:
  - Video Renderer
  - render_quote
tags:
  - automations
  - video
  - rendering
  - moviepy
---

# Quote Video Engine

Core video rendering engine. Takes a quote (text + author), background image, and background music — produces a 1080×1920 vertical social-media-style video with cinematic effects.

Located at `engine/quote-video-maker/render_quote.py`.

## Rendering Pipeline

```
render_quote_video(quote_text, author, bg_image_path, bg_music_path, output_path, config)
```

### Step-by-Step

1. **Load & process background** — PIL loads image, applies dark overlay (`110/255` opacity), resizes to 1080×1920
2. **Text wrapping** — wraps quote text to fit margins (60px left, 240px right — leaves space for mobile buttons)
3. **Typewriter animation** — reveals words one-by-one over `typing_duration` (default 2s)
4. **Ken Burns zoom** — slow zoom from 1.0× → 1.10× across full 5s duration
5. **Text rendering** — shadow layers (black) + white text, centered
6. **Author fade-in** — author name fades in after all quote words are revealed
7. **Audio processing** — loads background music, loops if shorter than 5s, trims to exactly 5s
8. **Video assembly** — MoviePy assembles frame sequence + audio → MP4 (`libx264` + `aac`)

> [!info] Frame-by-frame: Each reveal stage generates duplicated frames across its time slice for smooth playback at 24fps.

## Config — `config.json`

| Parameter | Value | Description |
|---|---|---|
| `width` | 1080 | Video width (px) |
| `height` | 1920 | Video height (px) |
| `fps` | 24 | Frames per second |
| `duration` | 5 | Total video duration (s) |
| `typing_duration` | 2 | Typewriter animation duration (s) |
| `font_size` | 68 | Quote text font size |
| `author_font_size` | 42 | Author font size |
| `line_spacing` | 1.45 | Line spacing multiplier |
| `shadow_offset` | 3 | Text shadow offset (px) |
| `overlay_opacity` | 110 | Dark overlay opacity (0-255) |
| `ken_burns_zoom_min` | 1.0 | Ken Burns start zoom |
| `ken_burns_zoom_max` | 1.10 | Ken Burns end zoom |

> [!tip] All rendering parameters are tunable in `config.json` without touching code.

## Effects

### Typewriter Effect
Words are revealed one at a time over 2 seconds. Each word appears with a slight visual step, creating a word-by-word build. Author name only appears after the full quote is revealed.

### Ken Burns Zoom
The background image slowly zooms from 1.0× to 1.10× over the full 5 seconds. Creates a subtle sense of motion on an otherwise static image.

### Audio
Background music is loaded, looped to fill the duration, volume adjusted, and mixed into the video. If the music track is shorter than 5s, it loops seamlessly.

## Related

- [[orchestration-layer]] — batch generation, asset pairing, state management
- [[main-app-flask#Quote Video API|Quote Video API Routes]]
- [[automations-home|Home]]
