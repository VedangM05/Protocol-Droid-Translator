"""Text-to-speech endpoint."""
import os
import tempfile
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api.deps import get_tts_engine

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    target_lang: str


@router.post("/tts")
def text_to_speech(request: Request, body: TTSRequest):
    """Generate speech from text in the given language; returns audio file URL or stream."""
    if not body.text or not body.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    tts = get_tts_engine(request)
    output_path = os.path.join(tempfile.gettempdir(), "bhasha_tts_output.mp3")
    path = tts.generate_speech(body.text, body.target_lang, output_path=output_path)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=500, detail="TTS generation failed")

    return FileResponse(
        path,
        media_type="audio/mpeg",
        filename="bhasha_tts.mp3",
    )
