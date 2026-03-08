# document_understanding/engine.py
import time
import spacy
from typing import Dict, Any

class DocumentUnderstandingLayer:
    def __init__(self):
        self.is_loaded = True
        try:
             self.nlp = spacy.load("en_core_web_sm")
        except:
             # Fallback if spacy model is not downloaded yet
             import os
             os.system("python -m spacy download en_core_web_sm")
             self.nlp = spacy.load("en_core_web_sm")
        print("Document Understanding Layer Initialized (Simulated).")

    def process(self, text: str, is_document: bool = False) -> Dict[str, Any]:
        """
        Simulates the Document Understanding Layer from the flowchart.
        """
        results = {}
        
        # 1. OCR (if scanned document)
        if is_document:
            results['OCR_Status'] = "Text Extracted via PyTesseract (Simulated)"
            
        # 2. Layout Parsing
        if is_document:
             results['Layout'] = "Headers, Paragraphs, Tables Identified (Simulated)"
        
        doc = self.nlp(text)
        
        # 3. Sentence Segmentation
        sentences = [sent.text for sent in doc.sents]
        results['Sentence_Segmentation'] = f"{len(sentences)} sentences found."
        
        # 4. Clause Detection (Simple split by commas/conjunctions for simulation)
        clauses = []
        for sent in sentences:
             clauses.extend([c.strip() for c in sent.split(',') if len(c.strip()) > 5])
        results['Clause_Detection'] = f"Extracted {len(clauses)} sub-clauses."
        
        # 5. POS Tagging
        pos_tags = [(token.text, token.pos_) for token in doc][:5] # Show first 5
        results['POS_Tagging'] = f"Sample Tags: {pos_tags}..."
        
        # 6. Dependency Parsing
        deps = [(token.text, token.dep_, token.head.text) for token in doc][:5]
        results['Dependency_Parsing'] = f"Sample Deps: {deps}..."
        
        # 7. Named Entity Recognition (NER++)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        results['NER++'] = entities if entities else "No entities found."
        
        # Output: Structured Document (we'll just return the dict for the UI)
        return results

doc_understanding_engine = DocumentUnderstandingLayer()
