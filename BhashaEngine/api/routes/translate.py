"""Translation and document translation endpoints."""
import os
import tempfile
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from api.deps import get_translation_engine

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str
    source_lang: str  # "Auto Detect" or language name
    target_lang: str
    domain: str = "General"


class TranslateResponse(BaseModel):
    text: str
    confidence: float
    detected_lang: dict | None = None
    enforced_terms: list[dict] = []


@router.post("/translate", response_model=TranslateResponse)
def translate_text(request: Request, body: TranslateRequest):
    """Translate text. If source_lang is 'Auto Detect', language is detected from text."""
    if not body.text or not body.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    engine = get_translation_engine(request)

    if body.source_lang == "Auto Detect":
        from api.deps import get_lang_detector
        detector = get_lang_detector(request)
        det = detector.detect_language(body.text)
        resolved_source = det.get("lang_name", "English")
        detected_lang = det
    else:
        resolved_source = body.source_lang
        detected_lang = None

    enforced_terms = []
    if "Healthcare" in body.domain:
        from glossary.medical_terms import apply_healthcare_glossary
        enforced_terms = apply_healthcare_glossary(
            text=body.text,
            target_lang_code=engine.get_nllb_code(body.target_lang),
        )

    result = engine.translate(
        text=body.text,
        source_lang=resolved_source,
        target_lang=body.target_lang,
    )

    if isinstance(result, dict):
        return TranslateResponse(
            text=result["text"],
            confidence=result.get("confidence", 0.0),
            detected_lang=detected_lang,
            enforced_terms=enforced_terms,
        )
    return TranslateResponse(
        text=result,
        confidence=0.0,
        detected_lang=detected_lang,
        enforced_terms=enforced_terms,
    )


ALLOWED_DOC_EXT = {".docx", ".xlsx", ".pptx"}


@router.post("/translate/document")
async def translate_document(
    request: Request,
    file: UploadFile = File(...),
    source_lang: str = Form("English"),
    target_lang: str = Form(...),
):
    """Upload a document (docx/xlsx/pptx); returns translated file download."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_DOC_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_DOC_EXT)}",
        )

    contents = await file.read()
    temp_path = os.path.join(tempfile.gettempdir(), f"bhasha_in_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(contents)

    try:
        engine = get_translation_engine(request)
        from translation.document_translator import DocumentTranslator
        doc_trans = DocumentTranslator(engine)

        if ext == ".docx":
            out_path = doc_trans.translate_docx(temp_path, source_lang, target_lang)
        elif ext == ".xlsx":
            out_path = doc_trans.translate_xlsx(temp_path, source_lang, target_lang)
        elif ext == ".pptx":
            out_path = doc_trans.translate_pptx(temp_path, source_lang, target_lang)
        else:
            raise HTTPException(status_code=400, detail="Unsupported document type")

        return FileResponse(
            out_path,
            media_type="application/octet-stream",
            filename=f"translated_{file.filename}",
        )
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
