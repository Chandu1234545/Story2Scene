from openai import OpenAI
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) # Logger for image_generation.py

load_dotenv()

class ImageModel:
    def __init__(self):
        logger.info("Initializing OpenAI image client")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set for ImageModel.")
        self.client = OpenAI(api_key=api_key)
        logger.info("Initialized OpenAI image client successfully")

    def generate_image_for_video(self, prompt: str, dir_name: str, img_name_base: str) -> str:
        """
        Generates an image from a given prompt using OpenAI's DALL-E 3
        and saves it to a JPG file.

        Args:
            prompt (str): The detailed prompt for image generation.
            dir_name (str): The directory where the image file should be saved.
            img_name_base (str): The base filename for the generated image (e.g., "scene_1").

        Returns:
            str: The full path to the saved image file.
        """
        full_image_path = os.path.join(dir_name, f"{img_name_base}.jpg")
        
        # Ensure the directory exists
        os.makedirs(dir_name, exist_ok=True)

        try:
            logger.info(f"Generating image for prompt: '{prompt[:50]}...'") # Log first 50 chars
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024", # DALL-E 3 supports 1024x1024, 1024x1792, 1792x1024
                quality="standard", # or "hd"
                n=1,
            )
            logger.info("Image generation response received.")
            image_url = response.data[0].url
            
            if not image_url:
                raise ValueError("No image URL returned by DALL-E API.")

            image_response = requests.get(image_url)
            image_response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

            image = Image.open(BytesIO(image_response.content))
            image.save(full_image_path)
            logger.info(f"Saved image to {full_image_path}")
            return full_image_path
        except requests.exceptions.RequestException as req_e:
            logger.error(f"Network or HTTP error fetching image from {image_url}: {req_e}", exc_info=True)
            self._create_dummy_image(full_image_path)
            return full_image_path
        except Exception as e:
            logger.error(f"Error generating or saving image to {full_image_path}: {str(e)}", exc_info=True)
            self._create_dummy_image(full_image_path)
            return full_image_path

    def _create_dummy_image(self, path: str):
        """Creates a black dummy image if actual image generation fails."""
        try:
            # Create a 1024x1024 black image
            dummy_image = Image.new('RGB', (1024, 1024), color = 'black')
            dummy_image.save(path)
            logger.warning(f"Created a black dummy image at {path} due to generation failure.")
        except Exception as dummy_e:
            logger.error(f"Failed to create dummy image at {path}: {dummy_e}")
            # If even dummy image creation fails, there's a serious problem, but we don't re-raise
            # to let the main process continue if possible.

if __name__ == "__main__":
    # Example usage when run directly (for testing)
    image_client = ImageModel()
    test_dir = "test_image_output"
    os.makedirs(test_dir, exist_ok=True)
    try:
        image_client.generate_image_for_video(
            "A futuristic city with flying cars and towering skyscrapers, sunset lighting, vibrant colors, cinematic view, highly detailed, octane render.",
            test_dir,
            "test_scene_image"
        )
    except Exception as e:
        logger.error(f"Test image generation failed: {e}")