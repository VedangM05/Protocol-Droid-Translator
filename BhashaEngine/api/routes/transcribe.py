"""Speech-to-text (transcription) endpoint."""
import os
import tempfile
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel

from api.deps import get_stt_engine

router = APIRouter()

ALLOWED_AUDIO_EXT = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}


class TranscribeResponse(BaseModel):
    text: str


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    """Upload an audio file; returns transcribed text (Whisper)."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_AUDIO_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_AUDIO_EXT)}",
        )

    contents = await file.read()
    temp_path = os.path.join(tempfile.gettempdir(), f"bhasha_upload_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(contents)

    try:
        stt = get_stt_engine(request)
        text = stt.transcribe(temp_path)
        return TranscribeResponse(text=text or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
