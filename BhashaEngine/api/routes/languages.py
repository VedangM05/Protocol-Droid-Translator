"""Language list and detect endpoints."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from api.deps import get_lang_detector

router = APIRouter()


class DetectRequest(BaseModel):
    text: str


class DetectResponse(BaseModel):
    lang: str
    lang_name: str
    confidence: float


@router.get("/languages")
def list_languages():
    """Return supported language names (for dropdowns)."""
    from translation.indictrans2_engine import LANG_CODE_MAP
    return {"languages": sorted(LANG_CODE_MAP.keys())}


@router.get("/languages/groups")
def list_language_groups():
    """Return languages grouped by region (for UI)."""
    from translation.indictrans2_engine import translation_engine
    engine = translation_engine  # load once for groups
    return engine.get_language_groups()


@router.post("/detect", response_model=DetectResponse)
def detect_language(request: Request, body: DetectRequest):
    """Detect language of the given text."""
    if not body.text or not body.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    detector = get_lang_detector(request)
    result = detector.detect_language(body.text)
    return DetectResponse(
        lang=result["lang"],
        lang_name=result["lang_name"],
        confidence=result["confidence"],
    )
