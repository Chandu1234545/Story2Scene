import os
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class MediaElement(BaseModel):
    """Class for defining multimedia elements of a scene"""
    image_prompt: str = Field(
        description="Detailed prompt for image generation that captures the essence of the scene"
    )
    audio_narration: str = Field(
        description="Text for text-to-speech narration that conveys the emotional tone of the scene"
    )
    background_music: str = Field(
        default="ambient",
        description="Type of background music for the scene (e.g., suspenseful, cheerful, melancholic)"
    )
    duration_seconds: float = Field(
        default=5.0,
        description="Suggested duration of this scene in seconds"
    )

class Scene(BaseModel):
    """Class for defining a scene in the story"""
    title: str = Field(
        description="Short descriptive title for the scene"
    )
    description: str = Field(
        description="Detailed description of what happens in the scene"
    )
    media: MediaElement = Field(
        description="Multimedia elements for the scene"
    )
    transition: str = Field(
        default="cut",
        description="Transition to the next scene (e.g., fade, dissolve, cut)"
    )

class StoryResponse(BaseModel):
    """Response model for generated story"""
    title: str = Field(description="Title of the story")
    theme: str = Field(description="Central theme of the story")
    scenes: List[Scene] = Field(description="List of scenes that compose the story")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the generated story"
    )

class StoryGenerator:
    """Generates structured stories for automatic video creation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the StoryGenerator with OpenAI API key"""
        self._initialize_llm(api_key)
        
    def _initialize_llm(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client"""
        try:
            # Use provided API key or get from environment
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
                
            if not api_key:
                raise ValueError("No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass api_key to constructor.")
                
            # Initialize OpenAI client
            self.client = OpenAI(api_key=api_key)
            self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o") # Changed default to gpt-4o for potentially better function calling
            logger.info(f"LLM initialized successfully with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise
            
    def _create_system_prompt(self) -> str:
        """Create the system prompt for story generation"""
        return """You are a creative storyteller and expert screenwriter specializing in creating engaging, visually compelling stories.

Your task is to generate a structured story that can be converted into a video sequence. Each story should be divided into distinct scenes that flow naturally together to tell a cohesive story.

For each scene, provide:
1. A title that captures the essence of the scene
2. A detailed description of what happens
3. Multimedia elements:
    - Image prompt: VERY detailed visual description for image generation with style, lighting, mood, colors, and details with proper synchronization with the audio narration. The image for the next scene should visually represent a continuation of the story.
    - Audio narration: Engaging narrative text for voice-over that advances the story and conveys emotion.
    - Background music suggestion
    - Suggested duration in seconds
4. Transition to the next scene

Important requirements:
- Each scene's audio narration should continue the story from the previous scene.
- Audio narration should sound like a professional storyteller.
- Image prompts should be extremely detailed for high-quality generation, including specific visual elements, composition, and artistic style.
- The story should have a clear beginning, middle, and end.
- The whole story when read through all scenes should feel cohesive and complete.
- Ensure the image prompts for consecutive scenes depict a logical progression of the story's visuals.
"""

    def _create_function_schema(self) -> Dict[str, Any]:
        """Create the function schema for story generation"""
        return {
            "name": "generate_story",
            "description": "Generate a structured story with scenes and multimedia elements for video creation",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the story"
                    },
                    "theme": {
                        "type": "string",
                        "description": "Central theme of the story"
                    },
                    "scenes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Short descriptive title for the scene"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Detailed description of what happens in the scene"
                                },
                                "media": {
                                    "type": "object",
                                    "properties": {
                                        "image_prompt": {
                                            "type": "string",
                                            "description": "Extremely detailed prompt for image generation that captures the essence of the scene with style, lighting, colors, mood, and specific visual details for DALL-E."
                                        },
                                        "audio_narration": {
                                            "type": "string",
                                            "description": "Engaging narrative text for voice-over that continues the story from the previous scene, flowing naturally."
                                        },
                                        "background_music": {
                                            "type": "string",
                                            "description": "Type of background music for the scene (e.g., suspenseful, cheerful, melancholic)"
                                        },
                                        "duration_seconds": {
                                            "type": "number",
                                            "description": "Suggested duration of this scene in seconds"
                                        }
                                    },
                                    "required": ["image_prompt", "audio_narration", "background_music", "duration_seconds"]
                                },
                                "transition": {
                                    "type": "string",
                                    "description": "Transition to the next scene (e.g., fade, dissolve, cut)"
                                }
                            },
                            "required": ["title", "description", "media", "transition"]
                        }
                    },
                },
                "required": ["title", "theme", "scenes"]
            }
        }

    def generate_story(self, prompt: str, num_scenes: int = 5, style: Optional[str] = None) -> StoryResponse:
        """
        Generate a structured story based on the input prompt
        
        Args:
            prompt: The user's story prompt or request
            num_scenes: Suggested number of scenes (default: 5)
            style: Optional style guidance (e.g., "dramatic", "comedic")
            
        Returns:
            StoryResponse object containing the structured story
        """
        try:
            logger.info(f"Generating story for prompt: {prompt}")
            
            # Prepare the messages
            user_prompt = f"Create a story with approximately {num_scenes} scenes based on the following prompt: {prompt}"
            if style:
                user_prompt += f"\nThe story should be in a {style} style."
                
            user_prompt += "\n\nMake sure each scene flows naturally from the previous one, with audio narration that continues the story and image prompts that are extremely detailed for high-quality generation."
                
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": user_prompt}
            ]
            
            # Call the OpenAI API with function calling
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=[{"type": "function", "function": self._create_function_schema()}],
                tool_choice={"type": "function", "function": {"name": "generate_story"}},
                temperature=0.7,
                max_tokens=3000
            )
            
            # Extract and parse the function call
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call:
                result = json.loads(tool_call.function.arguments)
                
                # Add metadata
                if "metadata" not in result:
                    result["metadata"] = {}
                    
                result["metadata"]["generation_timestamp"] = datetime.now().isoformat()
                result["metadata"]["prompt"] = prompt
                result["metadata"]["model"] = self.model_name
                
                # Convert to Pydantic model for validation
                story_response = StoryResponse(**result)
                logger.info(f"Successfully generated story '{story_response.title}' with {len(story_response.scenes)} scenes")
                
                return story_response
            else:
                raise ValueError("No function call in the response from OpenAI.")
                
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}", exc_info=True)
            raise

    def generate_story_legacy_format(self, message: str, num_scenes: int = 5) -> Dict[str, Any]:
        """
        Generate a story in the legacy format as per the provided template
        
        Args:
            message: The user's story prompt or request
            num_scenes: Suggested number of scenes
            
        Returns:
            Dictionary in the legacy format with scenes
        """
        try:
            # First generate structured story
            # For legacy, we don't pass 'style' from the StoryGenerator's perspective,
            # as the legacy format doesn't have a 'style' field explicitly.
            # The prompt will still guide the AI.
            story_response = self.generate_story(message, num_scenes)
            
            # Convert to legacy format
            legacy_format = {"response": {}}
            legacy_format["title"] = story_response.title
            legacy_format["theme"] = story_response.theme # Still include theme if desired
            for i, scene in enumerate(story_response.scenes, 1):
                scene_key = f"scene{i}"
                legacy_format["response"][scene_key] = {
                    "title": scene.title,
                    "description": scene.description,
                    "narration": scene.media.audio_narration,
                    "image_prompt": scene.media.image_prompt,
                    "background_music": scene.media.background_music,
                    "duration_seconds": scene.media.duration_seconds
                }
            
            logger.info("Successfully converted story to legacy format.")
            return legacy_format
            
        except Exception as e:
            logger.error(f"Error generating story in legacy format: {str(e)}", exc_info=True)
            raise

# The `generate_story_for_video` wrapper function is now removed from here,
# as the StoryGenerator class is initialized directly in app.py and its methods are called.
# This makes the `app.py` more explicit about which methods are being used.