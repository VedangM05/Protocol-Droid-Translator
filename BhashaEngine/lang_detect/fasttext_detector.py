# lang_detect/fasttext_detector.py
# Real language detection using langdetect library (pure Python, no C++ needed)

from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException

# Map ISO 639-1 codes to display names
ISO_TO_NAME = {
    "en": "English", "hi": "Hindi", "mr": "Marathi", "ta": "Tamil",
    "te": "Telugu", "bn": "Bengali", "gu": "Gujarati", "kn": "Kannada",
    "ml": "Malayalam", "pa": "Punjabi", "ur": "Urdu", "ne": "Nepali",
    "fr": "French", "de": "German", "es": "Spanish", "it": "Italian",
    "pt": "Portuguese", "nl": "Dutch", "ru": "Russian", "pl": "Polish",
    "cs": "Czech", "ro": "Romanian", "el": "Greek", "sv": "Swedish",
    "da": "Danish", "no": "Norwegian", "fi": "Finnish", "hu": "Hungarian",
    "uk": "Ukrainian", "bg": "Bulgarian", "hr": "Croatian", "sr": "Serbian",
    "sk": "Slovak", "sl": "Slovenian", "lt": "Lithuanian", "lv": "Latvian",
    "et": "Estonian", "ca": "Catalan", "gl": "Galician", "eu": "Basque",
    "ga": "Irish", "cy": "Welsh", "is": "Icelandic", "sq": "Albanian",
    "mk": "Macedonian", "bs": "Bosnian", "mt": "Maltese",
    "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)",
    "ja": "Japanese", "ko": "Korean", "vi": "Vietnamese", "th": "Thai",
    "id": "Indonesian", "ms": "Malay", "tl": "Filipino/Tagalog",
    "my": "Burmese", "km": "Khmer", "lo": "Lao",
    "ar": "Arabic", "he": "Hebrew", "tr": "Turkish", "fa": "Persian/Farsi",
    "sw": "Swahili", "am": "Amharic", "ha": "Hausa", "yo": "Yoruba",
    "ig": "Igbo", "zu": "Zulu", "so": "Somali", "af": "Afrikaans",
}


class LangDetector:
    def __init__(self):
        self.is_loaded = True
        print("Language Detector initialized (langdetect).")

    def detect_language(self, text: str) -> dict:
        """
        Detects the primary language of the input text.
        Returns: {'lang': 'en', 'lang_name': 'English', 'confidence': 0.98}
        """
        if not text or not text.strip():
            return {'lang': 'en', 'lang_name': 'English', 'confidence': 0.0}
        
        try:
            # Get all detected languages with probabilities
            results = detect_langs(text)
            if results:
                top = results[0]
                lang_code = str(top.lang)
                confidence = round(top.prob, 3)
                lang_name = ISO_TO_NAME.get(lang_code, lang_code.upper())
                return {
                    'lang': lang_code,
                    'lang_name': lang_name,
                    'confidence': confidence
                }
        except LangDetectException:
            pass
        
        return {'lang': 'en', 'lang_name': 'English', 'confidence': 0.0}

    def detect_all(self, text: str) -> list:
        """
        Returns all detected languages with their probabilities.
        """
        if not text or not text.strip():
            return []
        
        try:
            results = detect_langs(text)
            return [
                {
                    'lang': str(r.lang),
                    'lang_name': ISO_TO_NAME.get(str(r.lang), str(r.lang).upper()),
                    'confidence': round(r.prob, 3)
                }
                for r in results
            ]
        except LangDetectException:
            return []


# Singleton instance
lang_detector = LangDetector()
