import json
import random
from datetime import datetime
from pathlib import Path

from render_quote import render_quote_video, VIDEO_DURATION

BASE_DIR       = Path(__file__).parent
BG_IMAGE_DIR   = BASE_DIR / "bg-image"
BG_MUSIC_DIR   = BASE_DIR / "bg-music"
OUTPUT_DIR     = BASE_DIR / "output"
PROMPTS_DIR    = BASE_DIR / "prompts"
STATE_FILE     = BASE_DIR / "state.json"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
MUSIC_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".aac"}


def _load_batch_number() -> int:
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return int(data.get("next_batch", 1))
    except Exception:
        return 1


def _save_batch_number(n: int):
    STATE_FILE.write_text(json.dumps({"next_batch": n}, indent=2), encoding="utf-8")


def _scan_assets(folder, exts):
    try:
        return sorted([f for f in folder.iterdir() if f.suffix.lower() in exts])
    except Exception:
        return []


def _parse_quotes(raw_json: str):
    data = json.loads(raw_json.strip())
    quotes = data.get("quotes", [])
    result = []
    for q in quotes:
        text = (q.get("text") or "").strip()
        author = (q.get("author") or "").strip() or None
        if text:
            result.append({"text": text, "author": author})
    return result


def _format_author(author):
    return f"— {author}" if author else ""


def get_status():
    imgs   = _scan_assets(BG_IMAGE_DIR, IMAGE_EXTS)
    musics = _scan_assets(BG_MUSIC_DIR, MUSIC_EXTS)
    return {
        "bg_images": len(imgs),
        "bg_music": len(musics),
        "video_duration": VIDEO_DURATION,
        "state": {"next_batch": _load_batch_number()},
    }


def get_assets():
    imgs   = _scan_assets(BG_IMAGE_DIR, IMAGE_EXTS)
    musics = _scan_assets(BG_MUSIC_DIR, MUSIC_EXTS)
    return {
        "bg_images": [f.name for f in imgs],
        "bg_music": [f.name for f in musics],
    }


def get_config():
    cfg_path = BASE_DIR / "config.json"
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return {"error": "config.json not found or invalid"}


def get_master_prompt():
    p = PROMPTS_DIR / "master_prompt.txt"
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def batch_generate(quotes_json: str):
    quotes = _parse_quotes(quotes_json)
    if not quotes:
        return {"error": "No valid quotes found", "videos": []}

    imgs   = _scan_assets(BG_IMAGE_DIR, IMAGE_EXTS)
    musics = _scan_assets(BG_MUSIC_DIR, MUSIC_EXTS)

    if not imgs:
        return {"error": "No background images available"}
    if not musics:
        return {"error": "No background music available"}

    batch_offset = _load_batch_number()
    batches_in_run = (len(quotes) + 1) // 2
    _save_batch_number(batch_offset + batches_in_run)

    results = []
    for i, q in enumerate(quotes):
        text   = q["text"]
        author = _format_author(q["author"])

        bg_img   = random.choice(imgs)
        bg_music = random.choice(musics)

        ts       = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        batch    = batch_offset + (i // 2)
        slot     = (i % 2) + 1
        out_path = OUTPUT_DIR / f"{ts}_b{batch:04d}_s{slot}.mp4"

        try:
            render_quote_video(
                quote_text    = text,
                author_text   = author,
                bg_image_path = str(bg_img),
                bg_music_path = str(bg_music),
                output_path   = str(out_path),
            )
            results.append({
                "status": "ok",
                "filename": out_path.name,
                "text": text[:80],
                "author": author,
            })
        except Exception as e:
            results.append({
                "status": "error",
                "error": str(e),
                "text": text[:80],
            })

    return {"videos": results, "total": len(results), "success": sum(1 for r in results if r["status"] == "ok"), "failed": sum(1 for r in results if r["status"] == "error")}


def batch_generate_stream(quotes_json: str):
    quotes = _parse_quotes(quotes_json)
    if not quotes:
        yield json.dumps({"error": "No valid quotes found"})
        return

    imgs   = _scan_assets(BG_IMAGE_DIR, IMAGE_EXTS)
    musics = _scan_assets(BG_MUSIC_DIR, MUSIC_EXTS)

    if not imgs:
        yield json.dumps({"error": "No background images available"})
        return
    if not musics:
        yield json.dumps({"error": "No background music available"})
        return

    batch_offset = _load_batch_number()
    batches_in_run = (len(quotes) + 1) // 2
    _save_batch_number(batch_offset + batches_in_run)

    total = len(quotes)
    yield json.dumps({"type": "start", "total": total})

    results = []
    for i, q in enumerate(quotes):
        text   = q["text"]
        author = _format_author(q["author"])

        bg_img   = random.choice(imgs)
        bg_music = random.choice(musics)

        ts       = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        batch    = batch_offset + (i // 2)
        slot     = (i % 2) + 1
        out_path = OUTPUT_DIR / f"{ts}_b{batch:04d}_s{slot}.mp4"

        try:
            render_quote_video(
                quote_text    = text,
                author_text   = author,
                bg_image_path = str(bg_img),
                bg_music_path = str(bg_music),
                output_path   = str(out_path),
            )
            results.append({
                "status": "ok",
                "filename": out_path.name,
                "text": text[:80],
                "author": author,
            })
        except Exception as e:
            results.append({
                "status": "error",
                "error": str(e),
                "text": text[:80],
            })

        yield json.dumps({"type": "progress", "current": i + 1, "total": total, "text": text[:80], "filename": out_path.name})

    yield json.dumps({"type": "done", "videos": results, "total": len(results), "success": sum(1 for r in results if r["status"] == "ok"), "failed": sum(1 for r in results if r["status"] == "error")})