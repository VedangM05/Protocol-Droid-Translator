import re

# Healthcare domain glossary: explicitly enforce translations for critical medical terms
MEDICAL_GLOSSARY = {
    # English -> { Target Language Code -> Translated Term }
    "hypertension": {
        "hin_Deva": "उच्च रक्तचाप (Hypertension)",
        "mar_Deva": "उच्च रक्तदाब (Hypertension)",
        "ben_Beng": "উচ্চ রক্তচাপ (Hypertension)",
        "tam_Taml": "உயர் இரத்த அழுத்தம் (Hypertension)",
        "tel_Telu": "అధిక రక్తపోటు (Hypertension)",
    },
    "diabetes": {
        "hin_Deva": "मधुमेह (Diabetes)",
        "mar_Deva": "मधुमेह (Diabetes)",
        "ben_Beng": "ডায়াবেটিস (Diabetes)",
        "tam_Taml": "நீரிழிவு (Diabetes)",
        "tel_Telu": "మధుమేహం (Diabetes)",
    },
    "vaccine": {
        "hin_Deva": "टीका (Vaccine)",
        "mar_Deva": "लस (Vaccine)",
        "ben_Beng": "টিকা (Vaccine)",
        "tam_Taml": "தடுப்பூசி (Vaccine)",
        "tel_Telu": "టీకా (Vaccine)",
    },
    "antibiotics": {
        "hin_Deva": "एंटीबायोटिक्स (Antibiotics)",
        "mar_Deva": "अँटीबायोटिक्स (Antibiotics)",
        "ben_Beng": "অ্যান্টিবায়োটিক (Antibiotics)",
        "tam_Taml": "ஆண்டிபயாடிக்ஸ் (Antibiotics)",
        "tel_Telu": "యాంటీబయాటిక్స్ (Antibiotics)",
    },
    "symptoms": {
        "hin_Deva": "लक्षण",
        "mar_Deva": "लक्षणे",
        "ben_Beng": "লক্ষণ",
        "tam_Taml": "அறிகுறிகள்",
        "tel_Telu": "లక్షణాలు",
    },
    "prescription": {
        "hin_Deva": "नुस्खा (Prescription)",
        "mar_Deva": "प्रिस्क्रिप्शन",
        "ben_Beng": "প্রেসক্রিপশন",
        "tam_Taml": "மருந்துச் சீட்டு",
        "tel_Telu": "ప్రిస్క్రిప్షన్",
    }
}

def apply_healthcare_glossary(text: str, target_lang_code: str, is_source: bool = True) -> tuple:
    """
    If is_source is True: Scans English input for medical terms, returns a list of recognized terms.
    If is_source is False: Enforces the translation in the output text (if applicable).
    We will use a simpler approach: return the recognized terms to display in the UI.
    """
    recognized_terms = []
    
    # Simple regex search for terms in the text (case insensitive)
    for term, translations in MEDICAL_GLOSSARY.items():
        if re.search(r'\b' + re.escape(term) + r'\b', text, flags=re.IGNORECASE):
            if target_lang_code in translations:
                recognized_terms.append({
                    "term": term.title(),
                    "enforced_translation": translations[target_lang_code]
                })
                
    return recognized_terms
