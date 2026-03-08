from sentence_transformers import SentenceTransformer, util

class SBERTValidator:
    def __init__(self, model_name="paraphrase-multilingual-mpnet-base-v2"): # Improved accuracy model
        """
        Initializes the multilingual SBERT model for offline matching.
        """
        self.model_name = model_name
        print(f"Loading Validation Model: {self.model_name}...")
        try:
             self.model = SentenceTransformer(self.model_name)
             self.is_loaded = True
             print("Validation Model loaded successfully.")
        except Exception as e:
             print(f"Error loading SBERT model: {e}")
             self.is_loaded = False

    def validate_translation(self, original_text: str, back_translated_text: str) -> dict:
        """
        Computes the meaning validation checks.
        """
        if not self.is_loaded:
             return {"similarity_check": 0.0, "consistency_check": "Failed (model not loaded)", "threshold_verification": False}
             
        # SBERT Semantic Similarity Check
        embeddings1 = self.model.encode(original_text, convert_to_tensor=True)
        embeddings2 = self.model.encode(back_translated_text, convert_to_tensor=True)
        cosine_scores = util.cos_sim(embeddings1, embeddings2)
        score = round(cosine_scores[0][0].item(), 3)
        
        # Back-Translation Consistency Check
        consistency = "High" if score > 0.85 else "Low"
        
        # Threshold Verification
        threshold_passed = self.is_translation_acceptable(score)
        
        return {
             "similarity_check": score,
             "consistency_check": consistency,
             "threshold_verification": threshold_passed
        }

    def is_translation_acceptable(self, score: float, threshold=0.90) -> bool:
        return score >= threshold

# Singleton
semantic_validator = SBERTValidator()
