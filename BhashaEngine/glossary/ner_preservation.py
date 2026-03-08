import json
import os

# glossary/ner_preservation.py

class TerminologyPreserver:
    def __init__(self, glossary_path="glossary.json"):
        """
        Loads the rule-based JSON glossary to protect specific government/healthcare terms.
        """
        self.glossary_path = os.path.join(os.path.dirname(__file__), glossary_path)
        self.glossary = {}
        if os.path.exists(self.glossary_path):
             with open(self.glossary_path, "r", encoding="utf-8") as f:
                 self.glossary = json.load(f)

    def extract_and_protect(self, text: str) -> tuple:
        """
        Identifies protected terms using basic keyword matching (or NER in advanced cases).
        Returns the text to be passed to translator, and the dictionary of extracted entities.
        """
        protected_entities = {}
        placeholder_idx = 0
        
        # Note: In a real system you'd use spacy or customized NER
        # We do simple rule-based extraction for the hackathon
        processed_text = text
        for term, meta in self.glossary.items():
            if term.lower() in text.lower():
                placeholder = f"__PROTECTED_ENTITY_{placeholder_idx}__"
                # Store original context and its strict translation requirement
                protected_entities[placeholder] = meta
                
                # Case-insensitive replacement (rudimentary)
                import re
                processed_text = re.sub(term, placeholder, processed_text, flags=re.IGNORECASE)
                placeholder_idx += 1
                
        return processed_text, protected_entities

    def reinject(self, translated_text: str, entities: dict, target_lang: str) -> str:
        """
        Takes the translated text which has placeholders and injects the proper translated terminology.
        """
        final_text = translated_text
        for placeholder, meta in entities.items():
            # If the target language is in the glossary rule for this entity
            injection = meta.get(target_lang, meta.get("en", "Unknown Term"))
            final_text = final_text.replace(placeholder, injection)
            
        return final_text

term_preserver = TerminologyPreserver()
