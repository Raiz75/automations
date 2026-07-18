# automations/main/routes.py
"""
All Flask routes for the application.
Separated from app.py for better organization.
"""

from flask import jsonify, render_template, request, send_file, current_app, Response, stream_with_context
import os
import sys
import shutil

# Add engine directories to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_DIR = os.path.join(BASE_DIR, 'engine')
TTS_DIR = os.path.join(ENGINE_DIR, 'TTS')
QUOTE_VIDEO_DIR = os.path.join(ENGINE_DIR, 'quote-video-maker')
MP4_MP3_DIR = os.path.join(ENGINE_DIR, 'mp4-mp3-converter')
EXPLAINER_VIDEO_DIR = os.path.join(ENGINE_DIR, 'explainer-video-maker')

sys.path.insert(0, ENGINE_DIR)
sys.path.insert(0, TTS_DIR)
sys.path.insert(0, QUOTE_VIDEO_DIR)
sys.path.insert(0, MP4_MP3_DIR)
sys.path.insert(0, EXPLAINER_VIDEO_DIR)

# Import TTS functions
try:
    from tts_engine import generate_speech, get_status, VOICES
    TTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ TTS import error: {e}")
    TTS_AVAILABLE = False
    VOICES = []

try:
    from quote_video_engine import batch_generate, batch_generate_stream, get_status as qvm_status, get_assets as qvm_assets, get_config as qvm_config, get_master_prompt
    QUOTE_VIDEO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Quote Video import error: {e}")
    QUOTE_VIDEO_AVAILABLE = False

try:
    from engine import batch_convert_stream
    MP4_MP3_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MP4-MP3 Converter import error: {e}")
    MP4_MP3_AVAILABLE = False

try:
    from engine import get_status as evm_status, get_assets as evm_assets, get_master_prompts, render_video_stream
    EXPLAINER_VIDEO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Explainer Video Maker import error: {e}")
    EXPLAINER_VIDEO_AVAILABLE = False


# ============================================
# PROJECT CONFIGURATION
# ============================================
PROJECTS_CONFIG = {
    "text-to-speech": {
        "name": "Text to Speech",
        "icon": "🔊",
        "url": "/tts",
        "template": "tts.html",
        "enabled": True
    },
    "quote-video": {
        "name": "Quote Video Maker",
        "icon": "🎬",
        "url": "/quote-video",
        "template": "quote-video.html",
        "enabled": True
    },
    "mp4-mp3-converter": {
        "name": "MP4 to MP3 Converter",
        "icon": "🎵",
        "url": "/mp4-mp3-converter",
        "template": "mp4-mp3-converter.html",
        "enabled": True
    },
    "explainer-video": {
        "name": "Explainer Video Maker",
        "icon": "🎥",
        "url": "/explainer-video",
        "template": "explainer-video.html",
        "enabled": True
    },
}

# Navigation (auto-generated from PROJECTS_CONFIG)
NAVIGATION = [
    {"id": "overview", "name": "Overview", "url": "/", "icon": "🏠"}
]

for project_id, config in PROJECTS_CONFIG.items():
    if config.get("enabled", True):
        NAVIGATION.append({
            "id": project_id,
            "name": config["name"],
            "url": config["url"],
            "icon": config["icon"]
        })


def register_routes(app):
    """Register all routes with the Flask app."""
    
    # ============================================
    # VIEW ROUTES (Page Routes)
    # ============================================
    
    @app.route("/")
    def index():
        """Homepage / Overview"""
        return render_template("index.html", current_project_id="overview")
    
    @app.route("/tts")
    def tts_page():
        """TTS project page"""
        return render_template("tts.html", current_project_id="text-to-speech")
    
    @app.route("/quote-video")
    def quote_video_page():
        """Quote Video Maker project page"""
        return render_template("quote-video.html", current_project_id="quote-video")
    
    @app.route("/mp4-mp3-converter")
    def mp4_mp3_page():
        """MP4 to MP3 Converter project page"""
        return render_template("mp4-mp3-converter.html", current_project_id="mp4-mp3-converter")
    
    # ============================================
    # API ROUTES
    # ============================================
    
    @app.route("/api/navigation")
    def get_navigation():
        """Return navigation configuration"""
        return jsonify(NAVIGATION)
    
    @app.route("/api/projects")
    def list_projects():
        """List all projects"""
        projects = []
        for pid, config in PROJECTS_CONFIG.items():
            if config.get("enabled", True):
                projects.append({
                    "id": pid,
                    "name": config["name"],
                    "icon": config["icon"]
                })
        return jsonify(projects)
    
    # ============================================
    # TTS API ROUTES
    # ============================================
    
    @app.route("/api/tts/generate", methods=["POST"])
    def generate_tts_route():
        """Generate speech from text"""
        if not TTS_AVAILABLE:
            return jsonify({"error": "TTS module not available"}), 503
        
        try:
            data = request.json
            text = data.get("text", "").strip()
            voice = data.get("voice", "af_heart")
            
            if not text:
                return jsonify({"error": "Text is required"}), 400
            
            result = generate_speech(text, voice)
            return jsonify(result)
        
        except Exception as e:
            current_app.logger.error(f"TTS generation error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/tts/audio/<filename>")
    def get_tts_audio(filename):
        """Serve TTS audio files"""
        try:
            # Use the engine/TTS/output folder
            tts_output = os.path.join(ENGINE_DIR, "TTS", "output")
            file_path = os.path.join(tts_output, filename)
            
            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404
            
            return send_file(
                file_path,
                mimetype="audio/mpeg",
                as_attachment=False
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/tts/voices")
    def get_tts_voices():
        """Get available voices"""
        if TTS_AVAILABLE:
            return jsonify(VOICES)
        return jsonify([])
    
    @app.route("/api/tts/status")
    def tts_status():
        """Check TTS availability"""
        if TTS_AVAILABLE:
            return jsonify(get_status())
        return jsonify({"available": False, "error": "TTS module not loaded"})

    @app.route("/api/tts/preview/<voice>")
    def get_tts_preview(voice):
        """Get or generate a voice preview sample, cached to engine/TTS/voice-sample/"""
        if not TTS_AVAILABLE:
            return jsonify({"error": "TTS module not available"}), 503

        try:
            sample_dir = os.path.join(TTS_DIR, "voice-sample")
            os.makedirs(sample_dir, exist_ok=True)
            sample_path = os.path.join(sample_dir, f"{voice}.mp3")

            if os.path.exists(sample_path):
                return send_file(sample_path, mimetype="audio/mpeg")

            preview_text = f"Hello, this is {voice}. A girl named Sally sells sea shells by the shore. Her friend asks, 'How now, brown cow?' She laughs and says, 'Perfectly clear.' Test done."
            result = generate_speech(preview_text, voice)

            if result.get("success"):
                src = os.path.join(TTS_DIR, "output", result["filename"])
                if os.path.exists(src):
                    shutil.copy2(src, sample_path)
                    return send_file(sample_path, mimetype="audio/mpeg")

            return jsonify({"error": "Failed to generate preview"}), 500

        except Exception as e:
            current_app.logger.error(f"TTS preview error: {e}")
            return jsonify({"error": str(e)}), 500

    # ============================================
    # QUOTE VIDEO API ROUTES
    # ============================================

    @app.route("/api/quote-video/status")
    def quote_video_status():
        """Check Quote Video engine status"""
        if QUOTE_VIDEO_AVAILABLE:
            return jsonify(qvm_status())
        return jsonify({"available": False, "error": "Quote Video engine not loaded"})

    @app.route("/api/quote-video/assets")
    def quote_video_assets():
        """List available assets"""
        if QUOTE_VIDEO_AVAILABLE:
            return jsonify(qvm_assets())
        return jsonify({"bg_images": [], "bg_music": []})

    @app.route("/api/quote-video/config")
    def quote_video_config():
        """Get configuration"""
        if QUOTE_VIDEO_AVAILABLE:
            return jsonify(qvm_config())
        return jsonify({"error": "Engine not available"})

    @app.route("/api/quote-video/master-prompt")
    def quote_video_master_prompt():
        """Get the master prompt text"""
        if QUOTE_VIDEO_AVAILABLE:
            return jsonify({"prompt": get_master_prompt()})
        return jsonify({"prompt": ""})

    @app.route("/api/quote-video/generate", methods=["POST"])
    def quote_video_generate():
        """Batch generate quote videos from JSON with streaming progress"""
        if not QUOTE_VIDEO_AVAILABLE:
            return jsonify({"error": "Quote Video engine not available"}), 503

        try:
            data = request.json
            quotes_json = data.get("quotes_json", "").strip()
            if not quotes_json:
                return jsonify({"error": "quotes_json is required"}), 400

            def generate():
                for event in batch_generate_stream(quotes_json):
                    yield event + "\n"

            return Response(stream_with_context(generate()), mimetype="application/x-ndjson")

        except Exception as e:
            current_app.logger.error(f"Quote Video generation error: {e}")
            return jsonify({"error": str(e)}), 500

    # ============================================
    # MP4-MP3 CONVERTER API ROUTES
    # ============================================

    @app.route("/api/mp4-mp3-converter/convert", methods=["POST"])
    def mp4_mp3_convert():
        """Upload files and convert them to MP3"""
        if not MP4_MP3_AVAILABLE:
            return jsonify({"error": "Converter not available"}), 503

        try:
            if "files" not in request.files:
                return jsonify({"error": "No files provided"}), 400

            files = request.files.getlist("files")
            if not files:
                return jsonify({"error": "No files provided"}), 400

            mp4_mp3_dir = os.path.join(ENGINE_DIR, "mp4-mp3-converter")
            out_dir = os.path.join(mp4_mp3_dir, "output")

            saved = []
            for f in files:
                if f.filename:
                    safe_name = os.path.basename(f.filename)
                    dest = os.path.join(out_dir, safe_name)
                    f.save(dest)
                    saved.append(dest)

            if not saved:
                return jsonify({"error": "No valid files received"}), 400

            def generate():
                for event in batch_convert_stream(saved):
                    yield event + "\n"

            return Response(stream_with_context(generate()), mimetype="application/x-ndjson")

        except Exception as e:
            current_app.logger.error(f"MP4-MP3 conversion error: {e}")
            return jsonify({"error": str(e)}), 500

    # ============================================
    # EXPLAINER VIDEO API ROUTES
    # ============================================

    @app.route("/explainer-video")
    def explainer_video_page():
        """Explainer Video Maker project page"""
        return render_template("explainer-video.html", current_project_id="explainer-video")

    @app.route("/api/explainer-video/status")
    def explainer_video_status():
        """Check Explainer Video engine status"""
        if EXPLAINER_VIDEO_AVAILABLE:
            return jsonify(evm_status())
        return jsonify({"available": False, "error": "Explainer Video engine not loaded"})

    @app.route("/api/explainer-video/assets")
    def explainer_video_assets():
        """List available images"""
        if EXPLAINER_VIDEO_AVAILABLE:
            return jsonify(evm_assets())
        return jsonify({"images": []})

    @app.route("/api/explainer-video/master-prompts")
    def explainer_video_master_prompts():
        """Get the master prompt texts"""
        if EXPLAINER_VIDEO_AVAILABLE:
            return jsonify(get_master_prompts())
        return jsonify({"prompt1": "", "prompt2": "", "prompt3": ""})

    @app.route("/api/explainer-video/render", methods=["POST"])
    def explainer_video_render():
        """Render an explainer video from segments JSON with streaming progress"""
        if not EXPLAINER_VIDEO_AVAILABLE:
            return jsonify({"error": "Explainer Video engine not available"}), 503

        try:
            data = request.json
            segments_json = data.get("segments_json", "").strip()
            video_title = data.get("video_title", "").strip() or None
            details_json = data.get("details_json", "").strip() or None

            if not segments_json:
                return jsonify({"error": "segments_json is required"}), 400

            def generate():
                for event in render_video_stream(segments_json, video_title, details_json):
                    yield event + "\n"

            return Response(stream_with_context(generate()), mimetype="application/x-ndjson")

        except Exception as e:
            current_app.logger.error(f"Explainer Video render error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/explainer-video/output/<filename>")
    def get_explainer_video(filename):
        """Serve generated video files"""
        try:
            evm_output = os.path.join(EXPLAINER_VIDEO_DIR, "output")
            file_path = os.path.join(evm_output, filename)

            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            return send_file(
                file_path,
                mimetype="video/mp4",
                as_attachment=False
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/shutdown", methods=["POST"])
    def shutdown():
        """Kill the Python server process"""
        os._exit(0)

    @app.route("/api/quote-video/output/<filename>")
    def get_quote_video(filename):
        """Serve generated video files"""
        try:
            qvm_output = os.path.join(QUOTE_VIDEO_DIR, "output")
            file_path = os.path.join(qvm_output, filename)

            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            return send_file(
                file_path,
                mimetype="video/mp4",
                as_attachment=False
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500