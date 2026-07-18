# automations/main/app.py
"""
Main Flask application entry point.
Routes are imported from routes.py.
"""

from flask import Flask
import os
import sys

# Create Flask app
app = Flask(__name__)

# Add engine directories to Python path
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
sys.path.insert(0, BASE_DIR)

# Import and register routes
from routes import register_routes
register_routes(app)

# ============================================
# MAIN ENTRY POINT
# ============================================
if __name__ == "__main__":
    print("=" * 100)
    print("Python Project Hub")
    print("=" * 100)
    print(f"Working directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Engine directory: {ENGINE_DIR}")
    print(f"TTS directory: {TTS_DIR}")
    print(f"Quote Video directory: {QUOTE_VIDEO_DIR}")
    print(f"Explainer Video directory: {EXPLAINER_VIDEO_DIR}")
    print("=" * 100)
    app.run(debug=True, port=5001)