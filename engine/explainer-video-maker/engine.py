import json
import re
import os
from datetime import datetime
from pathlib import Path

BASE_DIR      = Path(__file__).parent
ASSETS_IMAGES = BASE_DIR / "assets" / "images"
CHAR_DIR      = BASE_DIR / "assets" / "character"
VIDEO_DIR     = BASE_DIR / "assets" / "video"
OUTPUT_DIR    = BASE_DIR / "output"
PROMPTS_DIR   = BASE_DIR / "prompts"
TTS_DIR       = BASE_DIR.parent / "TTS"

KOKORO_MODEL = TTS_DIR / "kokoro-v1.0.onnx"
KOKORO_VOICE = TTS_DIR / "voices-v1.0.bin"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

POSE_FILES = [
    "asking-charPose.png",
    "authority-charPose.png",
    "emphasis-charPose.png",
    "explaining-charPose.png",
    "pointingLeft-charPose.png",
]


def _parse_image_num(filename):
    m = re.match(r"(\d+)", filename)
    return int(m.group(1)) if m else None


def _build_image_map():
    result = {}
    try:
        for f in sorted(ASSETS_IMAGES.iterdir()):
            if f.suffix.lower() in IMAGE_EXTS:
                num = _parse_image_num(f.name)
                if num is not None:
                    result[num] = str(f)
    except Exception:
        pass
    return result


def _scan_images():
    try:
        return sorted(
            [f for f in ASSETS_IMAGES.iterdir() if f.suffix.lower() in IMAGE_EXTS],
            key=lambda f: _parse_image_num(f.name) or 999999,
        )
    except Exception:
        return []


def get_status():
    chars_exist = all((CHAR_DIR / f).is_file() for f in POSE_FILES)
    intro_path = VIDEO_DIR / "WonderSketch-intro.mp4"
    intro_exists = intro_path.is_file()
    model_ok = KOKORO_MODEL.is_file() and KOKORO_VOICE.is_file()
    images = _scan_images()
    return {
        "character_poses": chars_exist,
        "intro_video": intro_exists,
        "model_available": model_ok,
        "images_available": len(images),
        "images": [f.name for f in images],
    }


def get_assets():
    images = _scan_images()
    return {
        "images": [{"num": _parse_image_num(f.name), "name": f.name} for f in images if _parse_image_num(f.name) is not None],
        "character_poses": len(POSE_FILES),
    }


def get_master_prompts():
    prompts = {}
    for i in range(1, 4):
        p = PROMPTS_DIR / f"master_prompt{i}.txt"
        try:
            prompts[f"prompt{i}"] = p.read_text(encoding="utf-8")
        except Exception:
            prompts[f"prompt{i}"] = ""
    return prompts


def render_video_stream(segments_json: str, video_title: str = None, details_json: str = None):
    from render_explainer import render_explainer_video

    try:
        segments = json.loads(segments_json)
    except json.JSONDecodeError as e:
        yield json.dumps({"error": f"Invalid JSON: {e}"})
        return

    if not segments:
        yield json.dumps({"error": "Empty segments"})
        return

    image_map = _build_image_map()
    if not image_map:
        yield json.dumps({"error": "No images found in assets/images/ with numbered filenames"})
        return

    # Validate all referenced image numbers exist
    missing = set()
    for seg in segments:
        for micro in seg.get("microsegments", []):
            img_num = micro.get("image")
            if img_num is not None and img_num not in image_map:
                missing.add(img_num)
    if missing:
        yield json.dumps({"error": f"Image(s) not found: {sorted(missing)}"})
        return

    total_micro = sum(len(seg.get("microsegments", [])) for seg in segments)
    yield json.dumps({"type": "start", "total": total_micro})

    progress_log = []

    def log_fn(msg):
        progress_log.append(msg)

    def progress_fn(pct):
        pass

    def status_fn(msg):
        pass

    try:
        out_path = render_explainer_video(
            segments=segments,
            image_map=image_map,
            output_folder=str(OUTPUT_DIR),
            kokoro_model=str(KOKORO_MODEL),
            kokoro_voice=str(KOKORO_VOICE),
            log_fn=log_fn,
            progress_fn=progress_fn,
            status_fn=status_fn,
            video_title=video_title,
        )

        # Save .txt sidecar
        if details_json:
            try:
                details = json.loads(details_json)
                txt_name = os.path.splitext(os.path.basename(out_path))[0] + ".txt"
                txt_path = os.path.join(str(OUTPUT_DIR), txt_name)
                title = (details.get("title") or "").strip()
                desc  = (details.get("description") or "").strip()
                tags  = details.get("tags", [])
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"title:\n{title}\n\ndescription:\n{desc}\n\ntags:\n{', '.join(tags)}\n")
            except Exception:
                pass

        filename = os.path.basename(out_path)
        yield json.dumps({
            "type": "done",
            "filename": filename,
            "path": out_path,
            "logs": progress_log,
        })

    except Exception as e:
        yield json.dumps({"type": "error", "error": str(e), "logs": progress_log})
