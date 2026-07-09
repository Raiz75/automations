---
title: Frontend & UI
aliases:
  - UI
  - Templates
  - CSS
  - JavaScript
tags:
  - automations
  - frontend
  - ui
  - javascript
  - css
---

# Frontend & UI

Vanilla JS frontend with a three-panel layout: sidebar navigation, main content, and a bot console panel.

## Templates

All templates extend `_base.html` using Jinja2 blocks.

### `_base.html` — Master Layout

Three-panel structure:

```
┌──────────────┬─────────────────────┬──────────────────────┐
│              │                     │                      │
│   Sidebar    │   Content Area      │   Bot Console        │
│   (Nav)      │   (child template)  │   (Active Mode only) │
│              │                     │                      │
└──────────────┴─────────────────────┴──────────────────────┘
```

**Features:**
- Navigation loaded dynamically from `/api/navigation`
- Active Mode toggle — locks page interaction, shows bot console
- Toast notification system
- Dark mode support

### `index.html` — Overview Page

Landing page with project summary. Minimal — extends `_base.html` with overview content.

### `tts.html` — TTS Interface

- Textarea with clear button
- `Ctrl+Enter` shortcut to generate
- Voice picker: scrollable list of 54 voices with play-preview buttons
- Audio preview player (`<audio>` element)
- Status indicator dot (green/red/yellow)

### `quote-video.html` — Quote Video Interface

- Status display (asset counts, video duration)
- Copy Master Prompt button (fetches + clipboard API)
- JSON input textarea
- Asset summary (image/music counts)
- Generation log / progress
- Output list with download links

## JavaScript Interactions

| Feature | Mechanism |
|---|---|
| Navigation | `fetch('/api/navigation')` → populate sidebar |
| TTS Generate | `POST /api/tts/generate` → `fetch` → set audio source |
| Voice Preview | `GET /api/tts/preview/<voice>` → audio playback |
| Quote Gen | `POST /api/quote-video/generate` → display results |
| Copy Prompt | `fetch` → `navigator.clipboard.writeText()` |
| Active Mode | CSS overlay + panel toggle |
| Toast | DOM-created notification divs |

> [!tip] No frontend frameworks — everything is vanilla `fetch()`, DOM manipulation, and CSS transitions.

## CSS — `static/style.css` (826 lines)

| Section | Description |
|---|---|
| Layout | Three-panel grid, responsive breakpoint at 768px |
| Dark mode | `prefers-color-scheme: dark` media query |
| Sidebar | Navigation buttons with hover/active states |
| Voice picker | Scrollable list, selected state, preview buttons |
| Bot console | Dark terminal style, blinking cursor animation |
| Lock overlay | Full-screen overlay when Active Mode is on |
| Toast | Slide-in notifications, auto-dismiss |
| Animations | Pulse, spin, blink keyframes |

## Related

- [[main-app-flask|Main App (Flask)]]
- [[automations-home|Home]]
