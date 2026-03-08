# tts/coqui_engine.py
# Real TTS engine using gTTS (primary) + pyttsx3 (offline fallback)

import os
import tempfile

class TTSEngine:
    def __init__(self):
        self.gtts_available = False
        self.pyttsx3_available = False
        
        # Try to load gTTS
        try:
            from gtts import gTTS
            self.gtts_available = True
            print("gTTS loaded successfully.")
        except ImportError:
            print("gTTS not available.")
        
        # Try to load pyttsx3 as offline fallback
        try:
            import pyttsx3
            self.pyttsx3_available = True
            print("pyttsx3 loaded as offline TTS fallback.")
        except ImportError:
            print("pyttsx3 not available.")
        
        self.is_loaded = self.gtts_available or self.pyttsx3_available
    
    # Map display names to gTTS language codes
    GTTS_LANG_MAP = {
        "Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Telugu": "te",
        "Bengali": "bn", "Gujarati": "gu", "Kannada": "kn", "Malayalam": "ml",
        "Punjabi": "pa", "Urdu": "ur", "Nepali": "ne",
        "English": "en", "French": "fr", "German": "de", "Spanish": "es",
        "Italian": "it", "Portuguese": "pt", "Dutch": "nl", "Russian": "ru",
        "Polish": "pl", "Czech": "cs", "Romanian": "ro", "Greek": "el",
        "Swedish": "sv", "Danish": "da", "Norwegian": "no", "Finnish": "fi",
        "Hungarian": "hu", "Ukrainian": "uk", "Bulgarian": "bg", "Croatian": "hr",
        "Serbian": "sr", "Slovak": "sk", "Slovenian": "sl",
        "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
        "Japanese": "ja", "Korean": "ko", "Vietnamese": "vi", "Thai": "th",
        "Indonesian": "id", "Malay": "ms", "Filipino/Tagalog": "tl",
        "Burmese": "my", "Khmer": "km",
        "Arabic": "ar", "Hebrew": "he", "Turkish": "tr", "Persian/Farsi": "fa",
        "Swahili": "sw", "Amharic": "am", "Afrikaans": "af",
    }
    
    def _resolve_lang_code(self, target_lang: str) -> str:
        """Resolve language name to gTTS language code."""
        if target_lang in self.GTTS_LANG_MAP:
            return self.GTTS_LANG_MAP[target_lang]
        # Try direct (might already be an ISO code)
        return target_lang.lower()[:2]
    
    def generate_speech(self, text: str, target_lang: str, output_path: str = None) -> str:
        """
        Generates TTS audio and saves to an MP3 file.
        Returns the path to the generated audio file.
        """
        if not text or not text.strip():
            return None
            
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), "bhasha_tts_output.mp3")
        
        lang_code = self._resolve_lang_code(target_lang)
        
        # Try gTTS first (higher quality)
        if self.gtts_available:
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang=lang_code, slow=False)
                tts.save(output_path)
                print(f"TTS audio saved to: {output_path}")
                return output_path
            except Exception as e:
                print(f"gTTS failed: {e}, trying pyttsx3 fallback...")
        
        # Fallback to pyttsx3 (offline)
        if self.pyttsx3_available:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                # Save as wav since pyttsx3 doesn't support mp3
                wav_path = output_path.replace('.mp3', '.wav')
                engine.save_to_file(text, wav_path)
                engine.runAndWait()
                print(f"TTS audio (pyttsx3) saved to: {wav_path}")
                return wav_path
            except Exception as e:
                print(f"pyttsx3 also failed: {e}")
        
        return None


# Singleton
tts_engine = TTSEngine()
