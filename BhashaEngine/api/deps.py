"""
Dependency injection for lazy-loaded ML engines.
Engines are stored in app.state and loaded on first use.
"""
from fastapi import Request


def get_translation_engine(request: Request):
    """Get or lazy-load the NLLB translation engine."""
    if not hasattr(request.app.state, "translation_engine") or request.app.state.translation_engine is None:
        from translation.indictrans2_engine import translation_engine
        request.app.state.translation_engine = translation_engine
    return request.app.state.translation_engine


def get_stt_engine(request: Request):
    """Get or lazy-load the Whisper STT engine."""
    if not hasattr(request.app.state, "stt_engine") or request.app.state.stt_engine is None:
        from stt.whisper_engine import stt_engine
        request.app.state.stt_engine = stt_engine
    return request.app.state.stt_engine


def get_tts_engine(request: Request):
    """Get or lazy-load the TTS engine."""
    if not hasattr(request.app.state, "tts_engine") or request.app.state.tts_engine is None:
        from tts.coqui_engine import tts_engine
        request.app.state.tts_engine = tts_engine
    return request.app.state.tts_engine


def get_lang_detector(request: Request):
    """Get or lazy-load the language detector."""
    if not hasattr(request.app.state, "lang_detector") or request.app.state.lang_detector is None:
        from lang_detect.fasttext_detector import lang_detector
        request.app.state.lang_detector = lang_detector
    return request.app.state.lang_detector
