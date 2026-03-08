# BhashaEngine: Governance & Healthcare Access Platform

An offline, API-free, open-source AI translation and voice system designed for robust access to governance, healthcare, and legal information in rural and low-resource environments.

## Problem Statement
Millions of Indian citizens in rural areas cannot access essential government schemes, legal documents (like FIRs), or healthcare records due to language barriers and lack of internet connectivity. Existing platforms rely heavily on cloud APIs which fail in low-bandwidth zones and pose data privacy risks.

## Solution Architecture
Our system runs a 100% offline edge-AI pipeline:
1. **STT:** Whisper (Local)
2. **Lang Detect:** FastText
3. **Domain Classify:** IndicBERT
4. **Translation:** IndicTrans2
5. **Preservation:** Rule-based Glossary + NER
6. **Validation:** SBERT (Semantic Back-translation validation)
7. **TTS:** Coqui TTS

## Directory Structure
- `input/`: Handling raw audio and text.
- `stt/`: Whisper wrapper for localized STT transcribing.
- `lang_detect/`: FastText engine to detect source languages instantly.
- `domain_classification/`: IndicBERT context awareness.
- `translation/`: IndicTrans2 bidirectional translation.
- `glossary/`: Terminology preservation JSON to avoid mistranslating proper nouns.
- `validation/`: SBERT validator testing confidence via semantic similarity.
- `tts/`: Coqui voice output layer.
- `language_packs/`: Offline bhasha-pack loading system.

## Setup Instructions
1. Clone this repository to a local machine with at least 8GB RAM.
2. Ensure Python 3.9+ is installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. **Prerequisite: OCR Support (PDF Translation)**
   - Download Tesseract OCR for Windows: [Tesseract-OCR-w64-setup.exe](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install it (default path: `C:\Program Files\Tesseract-OCR`).
   - The application will automatically detect it.

5. *Important:* Download model weights into a local `/models` directory (Instructions inside `language_packs/`).
6. Run the web GUI offline:
   ```bash
   streamlit run app.py
   ```

## Model Justification
- **Whisper Base/Small:** Highly robust to Indian accents and background noise while remaining lightweight enough for consumer hardware.
- **IndicTrans2:** State-of-the-art government-backed dataset training ensuring formal and compliant translations.
- **FastText:** Ultra-fast sub-word character language identification taking <5ms per query.
- **SBERT:** Adds a crucial layer of trust by ensuring model hallucination is caught before showing results to a user.

## Hardware Requirements
- **Minimum:** 4-Core CPU, 8GB RAM, 5GB storage space (for single language pack).
- **Recommended (for faster inference):** NVIDIA GPU with 4GB+ VRAM, 16GB RAM.
