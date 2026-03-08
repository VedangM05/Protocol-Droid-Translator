# stt/whisper_engine.py
# Real Speech-to-Text engine using OpenAI Whisper (tiny model for speed)

import torch
import os

class OfflineSTTEngine:
    def __init__(self, model_id="openai/whisper-tiny"):
        """
        Initializes the Whisper model locally.
        Uses 'whisper-tiny' for faster CPU inference.
        """
        self.model_id = model_id
        self.pipe = None
        self.is_loaded = False
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"STT Engine initialized (model: {self.model_id}, device: {self.device})")
    
    def _ensure_loaded(self):
        """Lazy-load model on first use."""
        if not self.is_loaded:
            from transformers import pipeline
            print(f"Loading STT Model: {self.model_id}...")
            try:
                self.pipe = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_id,
                    chunk_length_s=30,
                    device=self.device,
                )
                self.is_loaded = True
                print("STT Model loaded successfully.")
            except Exception as e:
                print(f"Error loading STT model: {e}")
                raise

    def transcribe(self, audio_path: str) -> str:
        """
        Takes an audio file path (wav, mp3) and returns the transcribed text.
        Handles common audio format issues.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        self._ensure_loaded()
        
        # Try to load and convert audio if needed
        try:
            import soundfile as sf
            import numpy as np
            
            # Read using soundfile for better format support
            audio_data, sample_rate = sf.read(audio_path)
            
            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample to 16kHz if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                try:
                    import librosa
                    audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                    sample_rate = 16000
                except ImportError:
                    pass  # Will pass raw data, Whisper pipeline handles resampling
            
            # Pass audio array directly to pipeline
            result = self.pipe({"raw": audio_data.astype(np.float32), "sampling_rate": sample_rate})
            return result["text"].strip()
            
        except Exception as e:
            print(f"Soundfile loading failed ({e}), trying direct path...")
            # Fallback: pass file path directly (Whisper pipeline can handle it)
            try:
                result = self.pipe(audio_path)
                return result["text"].strip()
            except Exception as e2:
                raise Exception(f"Failed to transcribe audio: {e2}")


# Singleton instance — lazy loaded
stt_engine = OfflineSTTEngine()
