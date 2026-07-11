---
title: MP4 to MP3 Converter
aliases:
  - Vid Music Converter
  - FreeConvert
tags:
  - automations
  - conversion
  - audio
---

# MP4 to MP3 Converter

Converts video files to MP3 audio using the **FreeConvert API**. Located at `engine/mp4-mp3-converter/`.

## Architecture

```
User selects files → Upload to server → FreeConvert API → Download MP3 → Saved to output/
```

### Flow

1. **File selection** — user picks `.mp4`/`.mkv`/`.avi`/etc. files via browser file input
2. **Upload** — files are POSTed to `/api/mp4-mp3-converter/convert` as multipart form data
3. **FreeConvert job** — for each file, create a conversion job, upload, poll for completion, download MP3
4. **Streaming progress** — server yields NDJSON events after each file: `start`, `progress`, `done`
5. **Cleanup** — original video file deleted from `output/` after successful conversion
6. **Bot log** — every step logged to the bot console with timestamps

## Core File — `engine.py`

| Function | Description |
|---|---|
| `convert_file(video_path, output_path)` | Single file: create job → upload → poll → download |
| `batch_convert_stream(file_paths)` | Generator yielding NDJSON events per file |

### FreeConvert API

- Endpoint: `https://api.freeconvert.com/v1/process`
- Creates a 3-task job: `import/upload` → `convert` (mp4→mp3) → `export/url`
- Polls every 3s until completion (300s timeout)
- No API key required (free tier)

## Directories

| Directory | Purpose |
|---|---|
| `output/` | Generated MP3s + temporary video uploads (cleaned after conversion) |
| `converted/` | Videos moved here after successful conversion (archive) |

## API Routes

| Method | Path | Description |
|---|---|---|
| POST | `/api/mp4-mp3-converter/convert` | Upload files + stream conversion progress (NDJSON) |

## Events (NDJSON stream)

| Event | Fields |
|---|---|
| `start` | `{type, total}` |
| `progress` | `{type, current, total, name, filename}` |
| `done` | `{type, files[], total, success, failed}` |
| `error` | `{error}` |

## Related

- [[automations-home|Home]]
- [[main-app-flask#MP4-MP3 Converter API Routes|Flask Routes]]
