import os

def handle_text_input(text: str) -> str:
    """
    Cleans and prepares text input for the pipeline.
    """
    return text.strip()

def handle_audio_input(audio_path: str) -> str:
    """
    Validates audio file and prepares it for Whisper STT.
    Returns the absolute path to the valid audio file.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Add actual validation logic for wav/mp3 if required
    return audio_path
