from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # Logger for audio_generation.py

class AudioModel:
    def __init__(self):
        logger.info("Initializing OpenAI audio client")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set for AudioModel.")
        self.client = OpenAI(api_key=api_key)
        logger.info("Initialized OpenAI audio client successfully")

    def generate_audio_for_video(self, prompt: str, dir_name: str, audio_name: str) -> str:
        """
        Generates audio from a given prompt using OpenAI's TTS and saves it to a file.

        Args:
            prompt (str): The text to convert to speech.
            dir_name (str): The directory where the audio file should be saved.
            audio_name (str): The filename for the generated audio (e.g., "scene_1.mp3").

        Returns:
            str: The full path to the saved audio file.
        """
        full_audio_path = os.path.join(dir_name, audio_name)
        
        # Ensure the directory exists
        os.makedirs(dir_name, exist_ok=True)

        try:
            logger.info(f"Generating audio for: '{prompt[:50]}...'") # Log first 50 chars
            response = self.client.audio.speech.create(
                model="tts-1-hd", # High-quality TTS model
                voice="shimmer",  # Or 'alloy', 'echo', 'fable', 'onyx', 'nova'
                input=prompt,
                speed=0.90        # Adjust speech speed
            )
            logger.info("Audio generation response received.")

            with open(full_audio_path, "wb") as audio_file:
                for chunk in response.iter_bytes():
                    audio_file.write(chunk)
            logger.info(f"Saved audio to {full_audio_path}")
            return full_audio_path
        except Exception as e:
            logger.error(f"Error generating or saving audio to {full_audio_path}: {str(e)}", exc_info=True)
            # Create a dummy silent audio file to prevent video generation from crashing
            try:
                # Using pydub (requires ffmpeg)
                # from pydub import AudioSegment
                # silent_audio = AudioSegment.silent(duration=5000) # 5 seconds of silence
                # silent_audio.export(full_audio_path, format="mp3")
                
                # A simpler approach using moviepy's AudioFileClip for consistency and minimal new deps
                # This requires moviepy to be installed and ffmpeg accessible.
                # A 5-second silence clip
                from moviepy.editor import AudioFileClip
                dummy_audio = AudioFileClip("dummy_silent.mp3").set_duration(5) # Create a dummy silent clip
                dummy_audio.write_audiofile(full_audio_path)
                dummy_audio.close()
                logger.warning(f"Created a dummy silent audio file at {full_audio_path} due to error.")
                return full_audio_path
            except Exception as dummy_e:
                logger.error(f"Failed to create dummy audio file: {dummy_e}")
                raise # Re-raise original error if dummy creation also fails

if __name__ == "__main__":
    # Example usage when run directly (for testing)
    # This block will now create a dummy_silent.mp3 in the current directory first if not present
    # This dummy file is just for moviepy's internal use for a fallback if the real one fails.
    # It's better to ensure a proper audio generation or a silence function.
    # For a quick test, you might want a short valid audio file.
    
    # Create a dummy silent audio file if it doesn't exist for the MoviePy fallback in `generate_audio_for_video`
    if not os.path.exists("dummy_silent.mp3"):
        from pydub import AudioSegment
        silent_audio = AudioSegment.silent(duration=5000) # 5 seconds of silence
        silent_audio.export("dummy_silent.mp3", format="mp3")
        logger.info("Created dummy_silent.mp3 for fallback.")

    audio_client = AudioModel()
    test_dir = "test_audio_output"
    os.makedirs(test_dir, exist_ok=True)
    try:
        audio_client.generate_audio_for_video(
            "This is a test narration for the audio generation module.",
            test_dir,
            "test_scene_audio.mp3"
        )
    except Exception as e:
        logger.error(f"Test audio generation failed: {e}")