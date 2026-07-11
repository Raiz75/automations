import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

API_BASE = "https://api.freeconvert.com/v1/process"
POLL_INTERVAL = 3
POLL_TIMEOUT = 300

TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def _create_job():
    payload = {
        "tasks": {
            "import-1": {"operation": "import/upload"},
            "convert-1": {
                "operation": "convert",
                "input": "import-1",
                "input_format": "mp4",
                "output_format": "mp3",
            },
            "export-1": {"operation": "export/url", "input": ["convert-1"]},
        }
    }
    r = requests.post(
        f"{API_BASE}/jobs",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _get_upload_task(job):
    for t in job["tasks"]:
        if t["name"] == "import-1":
            return t
    raise RuntimeError("upload task not found in job response")


def _upload_file(file_path, upload_task):
    form = upload_task["result"]["form"]
    url = form["url"]
    params = form["parameters"]
    with open(file_path, "rb") as f:
        r = requests.post(url, data=params, files={"file": f}, timeout=120)
    r.raise_for_status()


def _poll_job(job_id):
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        r = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
        r.raise_for_status()
        data = r.json()
        if data["status"] == "completed":
            return data
        if data["status"] in ("error", "failed"):
            raise RuntimeError(f"Job failed: {data.get('message', 'unknown')}")
        time.sleep(POLL_INTERVAL)
    raise TimeoutError(f"Job did not complete within {POLL_TIMEOUT}s")


def _get_download_url(job):
    for t in job["tasks"]:
        if t.get("name") == "export-1":
            return t["result"]["url"]
    return job["tasks"][-1]["result"]["url"]


def _download_mp3(url, out_path):
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def convert_file(video_path, output_path):
    job = _create_job()
    job_id = job["id"]
    _upload_file(video_path, _get_upload_task(job))
    completed = _poll_job(job_id)
    _download_mp3(_get_download_url(completed), output_path)


def batch_convert_stream(file_paths):
    total = len(file_paths)
    if total == 0:
        yield json.dumps({"error": "No files provided"})
        return

    yield json.dumps({"type": "start", "total": total})

    results = []
    for i, video_path in enumerate(file_paths):
        path = Path(video_path)
        name = path.stem
        out_path = OUTPUT_DIR / f"{name}.mp3"
        if out_path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = OUTPUT_DIR / f"{name}_{ts}.mp3"

        try:
            convert_file(str(path), str(out_path))
            results.append({"status": "ok", "filename": out_path.name, "name": name})
        except Exception as e:
            results.append({"status": "error", "error": str(e), "name": name})
        finally:
            if path.exists():
                path.unlink()

        yield json.dumps({"type": "progress", "current": i + 1, "total": total, "name": name, "filename": out_path.name})

    yield json.dumps({"type": "done", "files": results, "total": len(results), "success": sum(1 for r in results if r["status"] == "ok"), "failed": sum(1 for r in results if r["status"] == "error")})
