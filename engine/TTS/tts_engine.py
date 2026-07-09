# automations/engine/TTS/tts_engine.py
"""
Text-to-Speech Engine
Located in engine/TTS/
"""

import os
from datetime import datetime
import soundfile as sf
from kokoro_onnx import Kokoro
from pydub import AudioSegment

# Configuration - paths relative to this file
TTS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(TTS_DIR, "output")
KOKORO_MODEL = os.path.join(TTS_DIR, "kokoro-v1.0.onnx")
KOKORO_VOICE = os.path.join(TTS_DIR, "voices-v1.0.bin")
SPEED = 1.0

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Full list of Kokoro v1.0 voices
VOICES = [
    # American English — Female
    "af_heart", "af_alloy", "af_aoede", "af_bella", "af_jessica",
    "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
    # American English — Male
    "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam",
    "am_michael", "am_onyx", "am_puck", "am_santa",
    # British English — Female
    "bf_alice", "bf_emma", "bf_isabella", "bf_lily",
    # British English — Male
    "bm_daniel", "bm_fable", "bm_george", "bm_lewis",
    # Japanese — Female
    "jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro",
    # Japanese — Male
    "jm_kumo",
    # Mandarin Chinese — Female
    "zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi",
    # Mandarin Chinese — Male
    "zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang",
    # Spanish
    "ef_dora", "em_alex", "em_santa",
    # French
    "ff_siwis",
    # Hindi — Female
    "hf_alpha", "hf_beta",
    # Hindi — Male
    "hm_omega", "hm_psi",
    # Italian
    "if_sara", "im_nicola",
]

DEFAULT_VOICE = "af_heart"


def generate_speech(text, voice=DEFAULT_VOICE):
    """Generate speech from text"""
    if not text:
        return {"error": "Text is required"}
    
    if voice not in VOICES:
        return {"error": f"Invalid voice selection: {voice}"}
    
    if not os.path.exists(KOKORO_MODEL):
        return {"error": f"Model not found: {KOKORO_MODEL}"}
    
    if not os.path.exists(KOKORO_VOICE):
        return {"error": f"Voice file not found: {KOKORO_VOICE}"}
    
    try:
        # Generate audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        wav_path = os.path.join(OUTPUT_FOLDER, f"tts_{timestamp}.wav")
        mp3_path = os.path.join(OUTPUT_FOLDER, f"tts_{timestamp}.mp3")
        
        kokoro = Kokoro(KOKORO_MODEL, KOKORO_VOICE)
        samples, sample_rate = kokoro.create(text, voice=voice, speed=SPEED, lang="en-us")
        
        sf.write(wav_path, samples, sample_rate)
        
        audio = AudioSegment.from_wav(wav_path)
        audio.export(mp3_path, format="mp3", bitrate="192k")
        
        os.remove(wav_path)
        
        return {
            "success": True,
            "audio_url": f"/api/tts/audio/{os.path.basename(mp3_path)}",
            "filename": os.path.basename(mp3_path)
        }
    
    except Exception as e:
        return {"error": str(e)}


def get_status():
    """Check if TTS is available"""
    model_exists = os.path.exists(KOKORO_MODEL)
    voice_exists = os.path.exists(KOKORO_VOICE)
    return {
        "available": model_exists and voice_exists,
        "model": model_exists,
        "voice": voice_exists,
        "model_path": KOKORO_MODEL,
        "voice_path": KOKORO_VOICE
    }


# For backward compatibility
__all__ = ['generate_speech', 'get_status', 'VOICES', 'DEFAULT_VOICE']