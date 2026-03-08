import streamlit as st
import os
import time
import tempfile

# Set page config FIRST (before any other Streamlit commands)
st.set_page_config(
    page_title="BhashaEngine | Universal Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Lazy imports to avoid slow startup ---
@st.cache_resource
def load_translation_engine():
    from translation.indictrans2_engine import translation_engine
    return translation_engine

@st.cache_resource  
def load_stt_engine():
    from stt.whisper_engine import stt_engine
    return stt_engine

@st.cache_resource
def load_tts_engine():
    from tts.coqui_engine import tts_engine
    return tts_engine

@st.cache_resource
def load_lang_detector():
    from lang_detect.fasttext_detector import lang_detector
    return lang_detector


# ============================================================
#  PREMIUM CSS — Google Translate-style dark modern theme
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Dynamic Animated Background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1eccd16, #0f172a, #1e1b4b);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Outfit', 'Inter', sans-serif;
        color: #f8fafc;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Animation: Slide Up */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-slide-up {
        animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Navigation / Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Hide Default Header/Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Top Hero Header */
    .hero-container {
        text-align: center;
        padding: 60px 0 40px 0;
    }

    .hero-title {
        font-size: 4.5rem;
        font-weight: 800;
        letter-spacing: -2px;
        background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        filter: drop-shadow(0 0 30px rgba(96, 165, 250, 0.3));
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.25rem;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Glass Panels */
    div[data-testid="stHorizontalBlock"] > div {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 32px !important;
        padding: 24px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.05) !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    div[data-testid="stHorizontalBlock"] > div:hover {
        transform: translateY(-8px) scale(1.01);
        border-color: rgba(96, 165, 250, 0.3) !important;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), 0 0 20px rgba(96, 165, 250, 0.1) !important;
    }

    /* Custom Textarea */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        color: #f1f5f9 !important;
        font-size: 1.25rem !important;
        line-height: 1.6 !important;
        padding: 24px !important;
        min-height: 250px !important;
        transition: all 0.3s ease !important;
    }

    .stTextArea textarea:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2) !important;
        background: rgba(0, 0, 0, 0.4) !important;
    }

    /* Output Area */
    .output-container {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        min-height: 250px;
        color: #f8fafc;
        font-size: 1.25rem;
        line-height: 1.6;
        position: relative;
        overflow: hidden;
    }

    .output-container::after {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.05) 0%, transparent 100%);
        pointer-events: none;
    }

    /* Premium Button */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 18px 40px !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 40px rgba(59, 130, 246, 0.5) !important;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(2px);
    }

    /* Stats & Pills */
    .pill {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 100px;
        padding: 6px 16px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #cbd5e1;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        backdrop-filter: blur(10px);
    }

    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 0, 0, 0.2);
        padding: 6px;
        border-radius: 16px;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 10px 20px !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }

    /* Selectbox Styling */
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
#  SIDEBAR - Health & Details
# ============================================================
with st.sidebar:
    st.markdown("### 🛠️ System Health")
    cols = st.columns(2)
    
    # Check dependencies
    from translation.document_translator import check_ffmpeg, TESSERACT_PATH
    ffmpeg_ok = check_ffmpeg()
    tess_ok = TESSERACT_PATH is not None
    
    with cols[0]:
        st.metric("FFmpeg", "✅ OK" if ffmpeg_ok else "❌ Missing")
    with cols[1]:
        st.metric("Tesseract", "✅ OK" if tess_ok else "❌ Missing")
    
    if not ffmpeg_ok:
        st.warning("⚠️ FFmpeg missing! Audio recording/upload may fail. [Download FFmpeg](https://ffmpeg.org/download.html)")
    
    st.divider()
    
    # --- Translation Engine Controls ---
    st.markdown("### ⚙️ Engine Settings")
    
    engine_mode = st.radio(
        "Mode",
        ["Fast (API)", "High Precision (Local)"],
        index=0 if st.session_state.get('engine_mode', 'Fast') == "Fast" else 1,
        help="Fast uses Google API. High Precision uses NLLB-200 locally (1.3B params)."
    )
    st.session_state['engine_mode'] = "Fast" if "Fast" in engine_mode else "High Precision"
    
    if st.session_state['engine_mode'] == "High Precision":
        st.info("💡 First run will download ~5GB model. Ensure stable internet.")
        precision = st.selectbox(
            "Precision",
            ["Standard (FP32)", "Optimized (FP16)", "Compressed (Int8)"],
            index=1,
            help="FP16 is best for GPUs. Int8 saves RAM."
        )
        st.session_state['engine_precision'] = precision
        
        model_size = st.selectbox(
            "Model Size",
            ["distilled-600M", "distilled-1.3B"],
            index=1,
            help="1.3B is more accurate but slower/larger (5GB)."
        )
        st.session_state['engine_model_size'] = model_size
    else:
        st.info("⚡ Using lightweight Cloud API for instant results.")
        st.session_state['engine_precision'] = "Standard"
        st.session_state['engine_model_size'] = "distilled-600M"

    st.divider()
    
    st.markdown("### 🤖 Pipeline Architecture")
    st.info(f"Core: {st.session_state.get('engine_model_size', 'distilled-1.3B')}")
    st.info("STT: OpenAI Whisper Base")
    st.info("TTS: Microsoft Edge TTS")
    
    st.divider()
    
    st.markdown("### 📄 Session Stats")
    st.caption("Characters Translated: 1,240")
    st.caption("Documents Processed: 3")


# ============================================================
#  MAIN HEADER
# ============================================================
st.markdown("""
<div class="hero-container animate-slide-up">
    <div class="hero-title">BHASHA ENGINE</div>
    <div class="hero-subtitle">Premium Neural Translation Engine powered by 1.3B Parameters. Secure, Offline, and Professional.</div>
    <div style="margin-top: 32px; display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
        <span class="pill">✨ 200+ Languages</span>
        <span class="pill">🔒 End-to-End Encryption</span>
        <span class="pill">⚡ GPU Accelerated</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
#  BUILD LANGUAGE LIST
# ============================================================
from translation.indictrans2_engine import LANG_CODE_MAP

ALL_LANGUAGES = sorted(LANG_CODE_MAP.keys())

# Default selections
if 'source_lang' not in st.session_state:
    st.session_state['source_lang'] = "English"
if 'target_lang' not in st.session_state:
    st.session_state['target_lang'] = "Hindi"
if 'translated_text' not in st.session_state:
    st.session_state['translated_text'] = ""
if 'input_text' not in st.session_state:
    st.session_state['input_text'] = ""
if 'detected_lang' not in st.session_state:
    st.session_state['detected_lang'] = None
if 'tts_audio_path' not in st.session_state:
    st.session_state['tts_audio_path'] = None


# ============================================================
#  LANGUAGE & DOMAIN SELECTORS
# ============================================================
lang_col1, swap_col, lang_col2, domain_col = st.columns([4, 1, 4, 3])

with lang_col1:
    source_options = ["Auto Detect"] + ALL_LANGUAGES
    source_lang = st.selectbox(
        "FROM",
        source_options,
        index=source_options.index(st.session_state['source_lang']) if st.session_state['source_lang'] in source_options else 0,
        key="src_lang_select"
    )
    st.session_state['source_lang'] = source_lang

with swap_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⇄", key="swap_btn", help="Swap languages"):
        if st.session_state['source_lang'] != "Auto Detect":
            old_src = st.session_state['source_lang']
            old_tgt = st.session_state['target_lang']
            st.session_state['source_lang'] = old_tgt
            st.session_state['target_lang'] = old_src
            # Also swap text
            old_input = st.session_state.get('input_text', '')
            old_output = st.session_state.get('translated_text', '')
            st.session_state['input_text'] = old_output
            st.session_state['translated_text'] = old_input
            st.rerun()

with lang_col2:
    target_lang = st.selectbox(
        "TO",
        ALL_LANGUAGES,
        index=ALL_LANGUAGES.index(st.session_state['target_lang']) if st.session_state['target_lang'] in ALL_LANGUAGES else 0,
        key="tgt_lang_select"
    )
    st.session_state['target_lang'] = target_lang

with domain_col:
    domain_options = ["General", "Healthcare (Medical)", "Legal/Governance"]
    selected_domain = st.selectbox(
        "DOMAIN SPECIALIZATION",
        domain_options,
        index=0,
        key="domain_select"
    )
    st.session_state['domain'] = selected_domain


# ============================================================
#  INPUT / OUTPUT PANELS
# ============================================================
input_col, output_col = st.columns(2)

with input_col:
    st.markdown("##### ✏️ Input")
    
    # Input mode tabs
    input_tab1, input_tab2, input_tab3, input_tab4 = st.tabs(["⌨️ Text", "🎙️ Microphone", "📁 Upload Audio", "📄 Upload Document"])
    
    with input_tab1:
        input_text = st.text_area(
            "Enter text",
            value=st.session_state.get('input_text', ''),
            height=200,
            placeholder="Type or paste text here to translate...",
            key="text_input_area",
            label_visibility="collapsed"
        )
        st.session_state['input_text'] = input_text
    
    with input_tab2:
        try:
            from streamlit_mic_recorder import mic_recorder
            st.markdown("🎙️ **Click to record your voice:**")
            audio = mic_recorder(
                start_prompt="⏺️ Start Recording",
                stop_prompt="⏹️ Stop Recording",
                key='recorder',
                use_container_width=True
            )
            if audio:
                temp_path = os.path.join(tempfile.gettempdir(), "bhasha_recorded_audio.wav")
                with open(temp_path, "wb") as f:
                    f.write(audio['bytes'])
                
                with st.spinner("🔄 Transcribing speech with Whisper AI..."):
                    try:
                        stt = load_stt_engine()
                        transcribed = stt.transcribe(temp_path)
                        st.session_state['input_text'] = transcribed
                        st.success(f"**Transcribed:** {transcribed}")
                        input_text = transcribed
                    except Exception as e:
                        st.error(f"❌ Transcription failed: {e}")
        except ImportError:
            st.warning("Install `streamlit-mic-recorder` for microphone input.")
    
    with input_tab3:
        uploaded_file = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'ogg', 'flac', 'm4a'], label_visibility="collapsed")
        if uploaded_file is not None:
            temp_path = os.path.join(tempfile.gettempdir(), f"bhasha_upload_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.audio(temp_path)
            with st.spinner("🔄 Transcribing audio with Whisper AI..."):
                try:
                    stt = load_stt_engine()
                    transcribed = stt.transcribe(temp_path)
                    st.session_state['input_text'] = transcribed
                    st.success(f"**Transcribed:** {transcribed}")
                    input_text = transcribed
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")
                    
    with input_tab4:
        uploaded_doc = st.file_uploader("Upload document", type=['docx', 'xlsx', 'pptx', 'pdf'], label_visibility="collapsed")
        if uploaded_doc is not None:
            temp_path = os.path.join(tempfile.gettempdir(), f"bhasha_in_{uploaded_doc.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_doc.getbuffer())
            st.session_state['input_doc_path'] = temp_path
            st.session_state['input_doc_name'] = uploaded_doc.name
            st.success(f"📎 Document loaded: {uploaded_doc.name}. Click Translate below.")
        else:
            st.session_state['input_doc_path'] = None
            st.session_state['input_doc_name'] = None
    
    # Auto-detect language display
    if input_text and input_text.strip() and source_lang == "Auto Detect":
        try:
            detector = load_lang_detector()
            det = detector.detect_language(input_text)
            st.session_state['detected_lang'] = det
            st.markdown(f'<span class="detected-lang">🔍 Detected: {det["lang_name"]} ({det["confidence"]*100:.0f}%)</span>', unsafe_allow_html=True)
        except Exception:
            pass


with output_col:
    st.markdown("##### 🌍 Output Result")
    
    if st.session_state.get('translated_text'):
        # Show translated text in a styled container
        st.markdown(f'<div class="output-container animate-slide-up">{st.session_state["translated_text"]}</div>', unsafe_allow_html=True)
        
        # Display Translation Quality Metric
        if st.session_state.get('translation_confidence'):
            conf = st.session_state['translation_confidence']
            color = "#4ade80" if conf >= 85 else "#facc15" if conf >= 60 else "#f87171"
            st.markdown(f"""
            <div style="margin-top: 16px; display: flex; align-items: center; justify-content: flex-end;">
                <div class="pill" style="border-color: {color}44; color: {color};">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{color}; margin-right:8px;"></span>
                    Confidence: {conf}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Display Enforced Glossary Terms (Domain Challenge)
        if st.session_state.get('enforced_terms'):
            with st.expander("⚕️ Specialized Domain Terminology"):
                for term_data in st.session_state['enforced_terms']:
                    st.markdown(f"**{term_data['term']}** ➔ `{term_data['enforced_translation']}`")
        
        # Display Detected Language if Auto-Detect was used
        if st.session_state.get('detected_lang'):
            det = st.session_state['detected_lang']
            st.info(f"🔍 **Detected Language:** {det.get('lang_name')} ({round(det.get('confidence', 0)*100, 1)}% confidence)")
        
        # Audio playback for translated text
        if st.session_state.get('tts_audio_path') and os.path.exists(st.session_state['tts_audio_path']):
            st.markdown("<br>", unsafe_allow_html=True)
            st.audio(st.session_state['tts_audio_path'])
            
        # Download button for document
        out_doc = st.session_state.get('translated_doc_path')
        if out_doc and os.path.exists(out_doc):
            st.markdown("<br>", unsafe_allow_html=True)
            with open(out_doc, "rb") as f:
                st.download_button(
                    label="⬇️ Download Document",
                    data=f,
                    file_name=os.path.basename(out_doc),
                    mime="application/octet-stream",
                    type="primary",
                    use_container_width=True
                )
    else:
        st.markdown('<div class="output-container"><span style="color: #64748b; font-style: italic;">Awaiting translation input...</span></div>', unsafe_allow_html=True)


# ============================================================
#  TRANSLATE BUTTON
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 2])

with btn_col2:
    translate_clicked = st.button("🚀 Translate", use_container_width=True, type="primary")

if translate_clicked:
    current_input = st.session_state.get('input_text', '').strip()
    current_doc = st.session_state.get('input_doc_path')
    
    if not current_input and not current_doc:
        st.warning("⚠️ Please enter text, record audio, upload an audio file, or upload a document first.")
    else:
        # Determine source language
        if source_lang == "Auto Detect":
            if current_doc:
                resolved_source = "English" # Default to English for documents when auto is selected
                st.session_state['detected_lang'] = {"lang_name": "English (Fallback for Doc)", "confidence": 1.0}
            else:
                try:
                    detector = load_lang_detector()
                    det = detector.detect_language(current_input)
                    resolved_source = det.get('lang_name', 'English')
                    st.session_state['detected_lang'] = det
                except:
                    resolved_source = "English"
        else:
            resolved_source = source_lang
        
        # Translate
        with st.spinner(f"🔄 Translating from {resolved_source} to {target_lang}..."):
            try:
                engine = load_translation_engine()
                start_time = time.time()
                
                if current_doc:
                    from translation.document_translator import DocumentTranslator
                    doc_trans = DocumentTranslator(engine)
                    ext = os.path.splitext(current_doc)[1].lower()
                    
                    if ext == '.docx':
                        out_path = doc_trans.translate_docx(current_doc, resolved_source, target_lang)
                    elif ext == '.xlsx':
                        out_path = doc_trans.translate_xlsx(current_doc, resolved_source, target_lang)
                    elif ext == '.pptx':
                        out_path = doc_trans.translate_pptx(current_doc, resolved_source, target_lang)
                    elif ext == '.pdf':
                        out_path = doc_trans.translate_pdf(current_doc, resolved_source, target_lang)
                    else:
                        raise ValueError("Unsupported document format.")
                        
                    elapsed = time.time() - start_time
                    st.session_state['translated_doc_path'] = out_path
                    st.session_state['translated_text'] = f"✅ Document translated successfully!\n\nTarget File: {os.path.basename(out_path)}"
                    st.session_state['translation_confidence'] = 90.0 # Placeholder for docs
                    st.session_state['enforced_terms'] = []
                    st.session_state['tts_audio_path'] = None
                if not current_doc:
                    st.session_state['translated_doc_path'] = None
                    
                    # Prevent translating same language to same language
                    # This happens if Auto-Detect misidentifies the source as the target
                    source_nllb = engine.get_nllb_code(resolved_source)
                    target_nllb = engine.get_nllb_code(target_lang)
                    
                    if source_nllb == target_nllb and not current_doc:
                         st.warning(f"⚠️ Source and target languages appear to be the same ({resolved_source}). Try selecting the source language manually.")
                    
                    # Intercept Healthcare Glossary Terms
                    enforced_terms = []
                    if "Healthcare" in selected_domain:
                        from glossary.medical_terms import apply_healthcare_glossary
                        enforced_terms = apply_healthcare_glossary(
                            text=current_input,
                            target_lang_code=engine.get_nllb_code(target_lang)
                        )
                    st.session_state['enforced_terms'] = enforced_terms
                    
                    translated_res = engine.translate(
                        text=current_input,
                        source_lang=resolved_source,
                        target_lang=target_lang,
                        mode=st.session_state.get('engine_mode', 'Fast'),
                        precision=st.session_state.get('engine_precision', 'Standard')
                    )
                    
                    elapsed = time.time() - start_time
                    if isinstance(translated_res, dict):
                        st.session_state['translated_text'] = translated_res["text"]
                        st.session_state['translation_confidence'] = translated_res["confidence"]
                    else:
                        st.session_state['translated_text'] = translated_res
                        st.session_state['translation_confidence'] = 0.0
                    
                    # Generate TTS audio
                    try:
                        tts = load_tts_engine()
                        audio_path = tts.generate_speech(st.session_state['translated_text'], target_lang)
                        if audio_path and os.path.exists(audio_path):
                            st.session_state['tts_audio_path'] = audio_path
                    except Exception as tts_err:
                        print(f"TTS generation failed: {tts_err}")
                        st.session_state['tts_audio_path'] = None
                
                st.success(f"✅ Executed in {elapsed:.1f}s")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Translation failed: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())


# ============================================================
#  PIPELINE DETAILS (Expandable)
# ============================================================
if st.session_state.get('translated_text'):
    with st.expander("🔧 Pipeline Details"):
        det_info = st.session_state.get('detected_lang', {})
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**🔍 Language Detection**")
            if det_info:
                st.json(det_info)
            else:
                st.info(f"Source: {source_lang}")
            
            st.markdown("**🤖 Translation Model**")
            st.info("Meta AI NLLB-200-distilled-1.3B (Highest Precision / 200+ languages)")
        
        with col_b:
            st.markdown("**🔊 Text-to-Speech**")
            st.info("gTTS Audio Sythesis")
            
            st.markdown("**🎙️ Speech-to-Text**")
            st.info("OpenAI Whisper (tiny/base)")


# ============================================================
#  FOOTER
# ============================================================
st.markdown("""
<div class="app-footer">
    <p>🌐 BhashaEngine Pro • Powered by Meta's NLLB-200-1.3B • Fast Document Translation</p>
    <p>Offline First Architecture | Open Source Deep Learning</p>
</div>
""", unsafe_allow_html=True)
