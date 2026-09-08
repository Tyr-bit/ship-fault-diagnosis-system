# audio_handler.py
import whisper
import tempfile
import os
from .config import WHISPER_MODEL

_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL)
    return _model

def transcribe_audio(audio_bytes):
    model = get_whisper_model()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        result = model.transcribe(tmp_path)
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)



