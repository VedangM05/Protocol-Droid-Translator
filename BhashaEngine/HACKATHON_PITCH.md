# HACKATHON_PITCH: BhashaEngine

## 1. PowerPoint Slide Outline
- **Slide 1: Title & Team** 
  - BhashaEngine: Offline, API-Free Language Access for Rural India.
- **Slide 2: The Problem**
  - "Language Barrier + Internet Barrier = Access Barrier." Citizens cannot register for crucial schemes or understand legal documents because systems are in English and require high-speed internet.
- **Slide 3: Our Solution**
  - A 100% local, edge-deployable AI appliance. Combines STT, Context-aware Translation, and TTS without a single API call.
- **Slide 4: Architecture (The Pipeline)**
  - Detail our 7-step architecture: Audio -> Whisper -> FastText -> IndicBERT -> IndicTrans2 & Glossary -> SBERT Validator -> Coqui TTS.
- **Slide 5: Innovation Highlights (Why we win)**
  - No Cloud = Data Privacy.
  - SBERT Semantic Validation = Trust/No Hallucination.
  - Context Aware = Medical terms translate differently than Legal terms.
  - Terminology Preservation = *FIR* is not badly translated into literal words; it stays *FIR*.
- **Slide 6: Tech Stack**
  - Streamlit, HuggingFace, PyTorch, IndicTrans2.
- **Slide 7: Future Scope & Scaling**
  - Distributing `.bhasha` translation packs via USB to local Panchayat offices!

---

## 2. Architecture Explanation for Judges
"Judges, the biggest flaw with standard translation APIs is that they fail offline and they hallucinate. Our Architecture is a strict sequential pipeline designed for **Trust**. We use IndicBERT to first detect the domain (legal vs health). If it's health, IndicTrans2 adjusts its vocabulary. We extract protected terms using our JSON NER glossary. Most importantly, before showing the result, SBERT back-translates the sentence to ensure the semantic meaning score is >90%."

---

## 3. Demo Flow Script
1. **Introduction (30s):** "Imagine a villager at a kiosk who only speaks Marathi and needs to know about Ayushman Bharat, but the internet is down."
2. **Text Input (1 min):** Type "The patient needs paracetamol and should apply for Ayushman Bharat."
   - *Show on screen:* It detects English, sees the domain "Healthcare", protects the term "Ayushman Bharat" using the glossary, and translates the rest to Marathi.
3. **Voice Input (1 min):** "Now let's use voice." Upload a short audio/speak into mic. Whisper transcribes. Show the translation and play the Coqui TTS output.
4. **Validation Demo (30s):** Show the "Pipeline Execution Log" to the judges highlighting the **SBERT similarity score of 0.94**, proving our AI evaluates itself.

---

## 4. Risks & Limitations section
- **Hardware Limitations:** Running all 6 models sequentially on a pure CPU might take 5-10 seconds per sentence. A Raspberry Pi might struggle.
- **Solution:** We quantized the models using ONNX/GGUF reducing memory load.
- **Glossary updating:** Requires manual JSON updates for new government schemes.
- **Solution:** Provide a highly simplified UI for admins to add terms to the JSON file.
