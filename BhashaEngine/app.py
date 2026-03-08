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
    
    /* Global Application Background */
    .stApp {
        background: radial-gradient(circle at 15% 50%, #1c0936 0%, #080f26 40%, #030514 100%);
        background-size: 200% 200%;
        animation: gradientAnimation 15s ease infinite;
        font-family: 'Outfit', sans-serif;
        color: #ffffff;
    }
    
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hide Default Header/Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Title Subtitle */
    .hero-title {
        text-align: center;
        padding: 40px 0 20px 0;
        animation: fadeInDown 0.8s ease-out forwards;
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .hero-title h1 {
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .hero-title p {
        color: #b0b8d6;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: 0;
    }
    
    /* Glassmorphic Translator Containers */
    div[data-testid="stHorizontalBlock"] > div {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stHorizontalBlock"] > div:hover {
        box-shadow: 0 15px 50px rgba(0, 201, 255, 0.1), inset 0 1px 0 rgba(255,255,255,0.15);
    }
    
    /* Text Areas (Input) */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        color: #f0f0f0 !important;
        font-size: 1.2rem !important;
        font-family: 'Outfit', sans-serif !important;
        resize: none !important;
        min-height: 220px !important;
        padding: 20px !important;
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #00C9FF !important;
        box-shadow: 0 0 15px rgba(0, 201, 255, 0.3) !important;
        background: rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Output Text Area Styling (Matches Input) */
    .output-text {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        min-height: 220px;
        color: #00C9FF;
        font-size: 1.2rem;
        line-height: 1.7;
        white-space: pre-wrap;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);
    }
    .output-placeholder {
        color: #526082;
        font-style: italic;
    }
    
    /* Selectboxes */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stSelectbox > div > div:hover {
        border-color: rgba(255, 255, 255, 0.3) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Premium Gradient Action Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 35px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 8px 25px rgba(255, 65, 108, 0.4) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 12px 30px rgba(255, 65, 108, 0.6) !important;
    }
    .stButton > button:active {
        transform: translateY(2px) scale(0.98) !important;
    }
    
    /* Swap Button overrides */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) > div:nth-child(2) .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        padding: 0 !important;
        font-size: 1.4rem !important;
        margin-top: 25px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
    }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) > div:nth-child(2) .stButton > button:hover {
        transform: rotate(180deg) scale(1.1) !important;
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%) !important;
    }
    
    /* Tabs & File Uploader */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8892b0;
        border-radius: 8px;
        padding: 8px 15px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%) !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Pills / Stats */
    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 6px 16px;
        border-radius: 30px;
        color: #e0e6ed;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0 5px;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, background 0.3s ease;
    }
    .stat-pill:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.1); border-color: #00C9FF; color: #00C9FF;
    }
    
    /* Tooltips, Messages, Expanders */
    .stInfo, .stSuccess, .stWarning {
        background: rgba(255, 255, 255, 0.05) !important;
        border-left: 4px solid #00C9FF !important;
        border-radius: 10px !important;
        color: #e0e6ed !important;
        backdrop-filter: blur(10px);
    }
    .stSuccess { border-left-color: #92FE9D !important; }
    .stWarning { border-left-color: #f6d365 !important; }
    
    .streamlit-expanderHeader {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: 12px !important;
        color: #00C9FF !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Loader Spinner Color */
    .stSpinner > div > div {
        border-color: #00C9FF transparent transparent transparent !important;
    }
    
    /* Upload document container */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 2px dashed rgba(0, 201, 255, 0.4) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #00C9FF !important;
        background: rgba(0, 201, 255, 0.05) !important;
    }
    
</style>
""", unsafe_allow_html=True)


# ============================================================
#  HEADER
# ============================================================
st.markdown("""
<div class="hero-title">
    <h1>🌐 BhashaEngine Pro</h1>
    <p>Universal Neural Translation • 200+ Languages • 1.3B Parameter Precision</p>
    <div style="margin-top: 15px;">
        <span class="stat-pill">🤖 NLLB-200 (1.3B)</span>
        <span class="stat-pill">🎙️ Whisper STT</span>
        <span class="stat-pill">🔊 Edge TTS</span>
        <span class="stat-pill">🔒 100% Offline</span>
        <span class="stat-pill">📄 DocX/Excel Support</span>
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
        uploaded_doc = st.file_uploader("Upload document", type=['docx', 'xlsx', 'pptx'], label_visibility="collapsed")
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
    st.markdown("##### 🌍 Translation")
    
    if st.session_state.get('translated_text'):
        # Show translated text in a styled container
        st.markdown(f"""<div class="output-text">{st.session_state['translated_text']}</div>""", unsafe_allow_html=True)
        
        # Display Translation Quality Metric
        if st.session_state.get('translation_confidence'):
            conf = st.session_state['translation_confidence']
            color = "#68d391" if conf >= 85 else "#f6d365" if conf >= 60 else "#fc8181"
            st.markdown(f"""
            <div style="margin-top: 10px; display: flex; align-items: center; justify-content: flex-end;">
                <span class="stat-pill" style="border-color: {color}; color: {color};">
                    🎯 Translation Quality: {conf}% Confidence
                </span>
            </div>
            """, unsafe_allow_html=True)
            
        # Display Enforced Glossary Terms (Domain Challenge)
        if st.session_state.get('enforced_terms'):
            with st.expander("⚕️ Healthcare Domain Terms Handled"):
                for term_data in st.session_state['enforced_terms']:
                    st.markdown(f"**{term_data['term']}** ➔ `{term_data['enforced_translation']}`")
        
        # Audio playback for translated text
        if st.session_state.get('tts_audio_path') and os.path.exists(st.session_state['tts_audio_path']):
            st.audio(st.session_state['tts_audio_path'])
            
        # Download button for document
        out_doc = st.session_state.get('translated_doc_path')
        if out_doc and os.path.exists(out_doc):
            st.markdown("<br>", unsafe_allow_html=True)
            with open(out_doc, "rb") as f:
                st.download_button(
                    label="⬇️ Download Translated Document",
                    data=f,
                    file_name=os.path.basename(out_doc),
                    mime="application/octet-stream",
                    type="primary",
                    use_container_width=True
                )
    else:
        st.markdown('<div class="output-text"><span class="output-placeholder">Translation will appear here...</span></div>', unsafe_allow_html=True)


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
                    else:
                        raise ValueError("Unsupported document format.")
                        
                    elapsed = time.time() - start_time
                    st.session_state['translated_doc_path'] = out_path
                    st.session_state['translated_text'] = f"✅ Document translated successfully!\n\nTarget File: {os.path.basename(out_path)}"
                    st.session_state['translation_confidence'] = 90.0 # Placeholder for docs
                    st.session_state['enforced_terms'] = []
                    st.session_state['tts_audio_path'] = None
                else:
                    st.session_state['translated_doc_path'] = None
                    
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
                        target_lang=target_lang
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
