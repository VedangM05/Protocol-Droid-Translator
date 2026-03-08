"""
BhashaEngine FastAPI backend.
Run: uvicorn main:app --reload --app-dir .
(from BhashaEngine directory, or: uvicorn main:app --reload --app-dir BhashaEngine)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import translate, transcribe, tts, languages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize app state for lazy-loaded engines (no heavy load at startup)."""
    app.state.translation_engine = None
    app.state.stt_engine = None
    app.state.tts_engine = None
    app.state.lang_detector = None
    yield
    # Optional: clear refs to help GC
    app.state.translation_engine = None
    app.state.stt_engine = None
    app.state.tts_engine = None
    app.state.lang_detector = None


app = FastAPI(
    title="BhashaEngine API",
    description="Offline neural translation, STT, TTS, and document processing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(languages.router, prefix="/api", tags=["languages"])
app.include_router(translate.router, prefix="/api", tags=["translate"])
app.include_router(transcribe.router, prefix="/api", tags=["transcribe"])
app.include_router(tts.router, prefix="/api", tags=["tts"])


@app.get("/")
def root():
    return {
        "service": "BhashaEngine API",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "languages": "GET /api/languages",
            "translate": "POST /api/translate",
            "translate_document": "POST /api/translate/document",
            "transcribe": "POST /api/transcribe",
            "tts": "POST /api/tts",
            "detect": "POST /api/detect",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "BhashaEngine"}
