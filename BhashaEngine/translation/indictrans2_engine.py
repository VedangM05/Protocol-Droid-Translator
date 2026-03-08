# translation/indictrans2_engine.py
# Real translation engine using Facebook's NLLB-200-distilled-1.3B
# Supports 200+ languages, runs fully offline after first model download

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# FLORES-200 language codes for NLLB-200
LANG_CODE_MAP = {
    # Indian Languages
    "Hindi": "hin_Deva",
    "Marathi": "mar_Deva",
    "Tamil": "tam_Taml",
    "Telugu": "tel_Telu",
    "Bengali": "ben_Beng",
    "Gujarati": "guj_Gujr",
    "Kannada": "kan_Knda",
    "Malayalam": "mal_Mlym",
    "Odia": "ory_Orya",
    "Punjabi": "pan_Guru",
    "Assamese": "asm_Beng",
    "Urdu": "urd_Arab",
    "Sanskrit": "san_Deva",
    "Nepali": "npi_Deva",
    "Sindhi": "snd_Arab",
    "Konkani": "kok_Deva",  # Not in NLLB but closest
    "Maithili": "mai_Deva",
    "Bodo": "brx_Deva",
    "Dogri": "doi_Deva",
    "Santali": "sat_Olck",
    
    # European Languages
    "English": "eng_Latn",
    "French": "fra_Latn",
    "German": "deu_Latn",
    "Spanish": "spa_Latn",
    "Italian": "ita_Latn",
    "Portuguese": "por_Latn",
    "Dutch": "nld_Latn",
    "Russian": "rus_Cyrl",
    "Polish": "pol_Latn",
    "Czech": "ces_Latn",
    "Romanian": "ron_Latn",
    "Greek": "ell_Grek",
    "Swedish": "swe_Latn",
    "Danish": "dan_Latn",
    "Norwegian": "nob_Latn",
    "Finnish": "fin_Latn",
    "Hungarian": "hun_Latn",
    "Ukrainian": "ukr_Cyrl",
    "Bulgarian": "bul_Cyrl",
    "Croatian": "hrv_Latn",
    "Serbian": "srp_Cyrl",
    "Slovak": "slk_Latn",
    "Slovenian": "slv_Latn",
    "Lithuanian": "lit_Latn",
    "Latvian": "lvs_Latn",
    "Estonian": "est_Latn",
    "Catalan": "cat_Latn",
    "Galician": "glg_Latn",
    "Basque": "eus_Latn",
    "Irish": "gle_Latn",
    "Welsh": "cym_Latn",
    "Icelandic": "isl_Latn",
    "Albanian": "als_Latn",
    "Macedonian": "mkd_Cyrl",
    "Bosnian": "bos_Latn",
    "Maltese": "mlt_Latn",
    
    # East Asian Languages
    "Chinese (Simplified)": "zho_Hans",
    "Chinese (Traditional)": "zho_Hant",
    "Japanese": "jpn_Jpan",
    "Korean": "kor_Hang",
    "Vietnamese": "vie_Latn",
    "Thai": "tha_Thai",
    "Indonesian": "ind_Latn",
    "Malay": "zsm_Latn",
    "Filipino/Tagalog": "tgl_Latn",
    "Burmese": "mya_Mymr",
    "Khmer": "khm_Khmr",
    "Lao": "lao_Laoo",
    
    # Middle Eastern & African Languages
    "Arabic": "arb_Arab",
    "Hebrew": "heb_Hebr",
    "Turkish": "tur_Latn",
    "Persian/Farsi": "pes_Arab",
    "Swahili": "swh_Latn",
    "Amharic": "amh_Ethi",
    "Hausa": "hau_Latn",
    "Yoruba": "yor_Latn",
    "Igbo": "ibo_Latn",
    "Zulu": "zul_Latn",
    "Somali": "som_Latn",
    "Afrikaans": "afr_Latn",
    
    # Central Asian
    "Kazakh": "kaz_Cyrl",
    "Uzbek": "uzn_Latn",
    "Georgian": "kat_Geor",
    "Armenian": "hye_Armn",
    "Azerbaijani": "azj_Latn",
    "Mongolian": "khk_Cyrl",
}

# Reverse map for looking up display name from code
CODE_TO_LANG = {v: k for k, v in LANG_CODE_MAP.items()}

# ISO 639-1 code to NLLB code mapping (for auto-detect integration)
ISO_TO_NLLB = {
    "en": "eng_Latn", "hi": "hin_Deva", "mr": "mar_Deva", "ta": "tam_Taml",
    "te": "tel_Telu", "bn": "ben_Beng", "gu": "guj_Gujr", "kn": "kan_Knda",
    "ml": "mal_Mlym", "or": "ory_Orya", "pa": "pan_Guru", "as": "asm_Beng",
    "ur": "urd_Arab", "sa": "san_Deva", "ne": "npi_Deva", "sd": "snd_Arab",
    "fr": "fra_Latn", "de": "deu_Latn", "es": "spa_Latn", "it": "ita_Latn",
    "pt": "por_Latn", "nl": "nld_Latn", "ru": "rus_Cyrl", "pl": "pol_Latn",
    "cs": "ces_Latn", "ro": "ron_Latn", "el": "ell_Grek", "sv": "swe_Latn",
    "da": "dan_Latn", "no": "nob_Latn", "fi": "fin_Latn", "hu": "hun_Latn",
    "uk": "ukr_Cyrl", "bg": "bul_Cyrl", "hr": "hrv_Latn", "sr": "srp_Cyrl",
    "sk": "slk_Latn", "sl": "slv_Latn", "lt": "lit_Latn", "lv": "lvs_Latn",
    "et": "est_Latn", "ca": "cat_Latn", "gl": "glg_Latn", "eu": "eus_Latn",
    "ga": "gle_Latn", "cy": "cym_Latn", "is": "isl_Latn", "sq": "als_Latn",
    "mk": "mkd_Cyrl", "bs": "bos_Latn", "mt": "mlt_Latn",
    "zh": "zho_Hans", "ja": "jpn_Jpan", "ko": "kor_Hang", "vi": "vie_Latn",
    "th": "tha_Thai", "id": "ind_Latn", "ms": "zsm_Latn", "tl": "tgl_Latn",
    "my": "mya_Mymr", "km": "khm_Khmr", "lo": "lao_Laoo",
    "ar": "arb_Arab", "he": "heb_Hebr", "tr": "tur_Latn", "fa": "pes_Arab",
    "sw": "swh_Latn", "am": "amh_Ethi", "ha": "hau_Latn", "yo": "yor_Latn",
    "ig": "ibo_Latn", "zu": "zul_Latn", "so": "som_Latn", "af": "afr_Latn",
    "kk": "kaz_Cyrl", "uz": "uzn_Latn", "ka": "kat_Geor", "hy": "hye_Armn",
    "az": "azj_Latn", "mn": "khk_Cyrl",
}


class NLLB200TranslationEngine:
    """
    Real translation engine using Facebook's NLLB-200-distilled-1.3B for high precision offline translation.
    Supports 200+ languages. Runs fully offline after first model download.
    """
    
    def __init__(self, model_name="facebook/nllb-200-distilled-1.3B"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_fp16 = torch.cuda.is_available()  # FP16 on GPU only
        print(f"NLLB-200 Translation Engine initialized (device: {self.device})")
        
    def _ensure_loaded(self):
        """Lazy-load the model on first use to avoid slow startup."""
        if not self.is_loaded:
            print(f"Loading NLLB-200 model: {self.model_name}...")
            print("This may take a few minutes on first run (downloading ~5GB model for enhanced precision)...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            if self.use_fp16:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name, torch_dtype=torch.float16
                )
            else:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                # Apply dynamic quantization for CPU to dramatically speed up inference
                self.model = torch.quantization.quantize_dynamic(
                    self.model, {torch.nn.Linear}, dtype=torch.qint8
                )
            
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            print("NLLB-200 model loaded successfully!")
    
    def get_nllb_code(self, lang_input: str) -> str:
        """
        Resolves a language name, ISO code, or NLLB code to a valid NLLB code.
        """
        # Already a valid NLLB code
        if lang_input in CODE_TO_LANG:
            return lang_input
        
        # Display name lookup
        if lang_input in LANG_CODE_MAP:
            return LANG_CODE_MAP[lang_input]
        
        # ISO code lookup
        if lang_input in ISO_TO_NLLB:
            return ISO_TO_NLLB[lang_input]
        
        # Try case-insensitive match on display names
        for name, code in LANG_CODE_MAP.items():
            if name.lower() == lang_input.lower():
                return code
        
        # Fallback: return as-is (might be a valid NLLB code we didn't map)
        return lang_input
    
    def translate(self, text: str, source_lang: str, target_lang: str, domain: str = "General") -> str:
        """
        Translates text from source_lang to target_lang using NLLB-200.
        
        Args:
            text: The text to translate
            source_lang: Source language (name, ISO code, or NLLB code)
            target_lang: Target language (name, ISO code, or NLLB code)
            domain: Domain context (for future use)
            
        Returns:
            Translated text string
        """
        if not text or not text.strip():
            return ""
            
        self._ensure_loaded()
        
        src_code = self.get_nllb_code(source_lang)
        tgt_code = self.get_nllb_code(target_lang)
        
        # For long text, split into sentences and translate individually (much faster)
        sentences = self._split_sentences(text)
        if len(sentences) > 1:
            translated_parts = []
            avg_conf = []
            for sent in sentences:
                if sent.strip():
                    res = self._translate_single(sent, src_code, tgt_code)
                    translated_parts.append(res["text"])
                    if res["confidence"] > 0:
                        avg_conf.append(res["confidence"])
                        
            final_conf = sum(avg_conf) / len(avg_conf) if avg_conf else 0.0
            return {"text": " ".join(translated_parts), "confidence": round(final_conf, 1)}
        else:
            return self._translate_single(text, src_code, tgt_code)
    
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences for faster per-sentence translation."""
        import re
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
    
    def _translate_single(self, text: str, src_code: str, tgt_code: str) -> str:
        """Translate a single sentence/chunk — optimized for speed."""
        # Set source language for tokenizer
        self.tokenizer.src_lang = src_code
        
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get target language token ID
        tgt_lang_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
        
        # Generate translation with scores
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_new_tokens=256,
                num_beams=1,
                do_sample=False,
                return_dict_in_generate=True,
                output_scores=True
            )
            
            # Calculate simple confidence score based on generation probabilities
            confidence_score = 0.0
            if outputs.scores:
                try:
                    # Average max logit probabilities mapped to 0-100% roughly
                    probs = [torch.nn.functional.softmax(score, dim=-1).max().item() for score in outputs.scores]
                    confidence_score = (sum(probs) / len(probs)) * 100
                    confidence_score = round(confidence_score, 1)
                except Exception as e:
                    print("Could not compute confidence score", e)
        
        # Decode
        result = self.tokenizer.batch_decode(outputs.sequences, skip_special_tokens=True)
        return {"text": result[0] if result else "", "confidence": confidence_score}
        
    def translate_batch(self, texts: list, source_lang: str, target_lang: str) -> list:
        """Translate a batch of strings efficiently"""
        if not texts:
            return []
            
        self._ensure_loaded()
        src_code = self.get_nllb_code(source_lang)
        tgt_code = self.get_nllb_code(target_lang)
        
        self.tokenizer.src_lang = src_code
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=256)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        tgt_lang_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_new_tokens=256,
                num_beams=1,
                do_sample=False,
                return_dict_in_generate=True,
                output_scores=True
            )
            
            # Confidence for batch (taking average over tokens, identical for all in batch for simplicity)
            confidence_score = 0.0
            if outputs.scores:
                try:
                    probs = [torch.nn.functional.softmax(score, dim=-1).max().item() for score in outputs.scores]
                    confidence_score = round((sum(probs) / len(probs)) * 100, 1)
                except:
                    pass
            
        results = self.tokenizer.batch_decode(outputs.sequences, skip_special_tokens=True)
        return [{"text": r, "confidence": confidence_score} for r in results]
    
    def get_supported_languages(self) -> list:
        """Returns list of supported language display names."""
        return sorted(LANG_CODE_MAP.keys())
    
    def get_language_groups(self) -> dict:
        """Returns languages grouped by region for UI dropdowns."""
        groups = {
            "🇮🇳 Indian Languages": [
                "Hindi", "Marathi", "Tamil", "Telugu", "Bengali", "Gujarati",
                "Kannada", "Malayalam", "Odia", "Punjabi", "Assamese", "Urdu",
                "Sanskrit", "Nepali", "Sindhi", "Maithili", "Santali", "Dogri", "Bodo"
            ],
            "🌍 European Languages": [
                "English", "French", "German", "Spanish", "Italian", "Portuguese",
                "Dutch", "Russian", "Polish", "Czech", "Romanian", "Greek",
                "Swedish", "Danish", "Norwegian", "Finnish", "Hungarian", "Ukrainian",
                "Bulgarian", "Croatian", "Serbian", "Slovak", "Slovenian",
                "Lithuanian", "Latvian", "Estonian", "Catalan", "Galician",
                "Basque", "Irish", "Welsh", "Icelandic", "Albanian",
                "Macedonian", "Bosnian", "Maltese"
            ],
            "🌏 East Asian Languages": [
                "Chinese (Simplified)", "Chinese (Traditional)", "Japanese",
                "Korean", "Vietnamese", "Thai", "Indonesian", "Malay",
                "Filipino/Tagalog", "Burmese", "Khmer", "Lao"
            ],
            "🌍 Middle Eastern & African": [
                "Arabic", "Hebrew", "Turkish", "Persian/Farsi", "Swahili",
                "Amharic", "Hausa", "Yoruba", "Igbo", "Zulu", "Somali", "Afrikaans"
            ],
            "🌐 Central Asian": [
                "Kazakh", "Uzbek", "Georgian", "Armenian", "Azerbaijani", "Mongolian"
            ]
        }
        return groups


# Singleton instance
translation_engine = NLLB200TranslationEngine()
