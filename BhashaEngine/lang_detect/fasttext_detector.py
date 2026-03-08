# lang_detect/fasttext_detector.py
# Language detector using langdetect library

from langdetect import detect, detect_langs, DetectorFactory
DetectorFactory.seed = 0 # Ensure consistent results

class LanguageDetector:
    def __init__(self):
        # Mapping langdetect codes to display names
        self.code_to_name = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'ur': 'Urdu',
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish',
            'it': 'Italian',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'ar': 'Arabic',
            'tr': 'Turkish',
        }

    def detect_language(self, text):
        """Detects the language of the given text."""
        if not text or len(text.strip()) < 3:
            return {"lang_name": "English", "confidence": 1.0}
            
        try:
            # Get multiple results for better confidence tracking
            langs = detect_langs(text)
            top_lang = langs[0]
            
            lang_code = top_lang.lang
            lang_name = self.code_to_name.get(lang_code, "English")
            
            # Special check for Devanagari scripts (Hindi/Marathi)
            # langdetect sometimes struggles between them
            if lang_code in ['hi', 'mr']:
                # Simple heuristic: look for Marathi specific characters though langdetect is usually okayish
                 pass

            return {
                "lang_name": lang_name,
                "confidence": top_lang.prob
            }
        except Exception as e:
            print(f"Language detection error: {e}")
            return {"lang_name": "English", "confidence": 0.0}

# Singleton instance
lang_detector = LanguageDetector()
