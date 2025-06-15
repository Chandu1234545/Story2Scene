import os
import logging
# from moviepy.editor import ProgressBar
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, ColorClip
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_video(project_dir: str, scene_numbers: list[int], output_filename: str = "final_video.mp4") -> str | None:
    """
    Combines generated images and audio into a final video.
    Assumes image and audio files are named 'scene_X.jpg' and 'scene_X.mp3' in project_dir.
    
    Returns:
        Path to the saved final video file, or None if generation fails.
    """
    target_width, target_height = 1280, 720
    video_size = (target_width, target_height)
    fps = 30
    clips = []

    for scene_num in scene_numbers:
        image_path = os.path.join(project_dir, f"scene_{scene_num}.jpg")
        audio_path = os.path.join(project_dir, f"scene_{scene_num}.mp3")

        img_clip = None
        audio_clip = None
        scene_duration = 5.0  # default duration if no audio

        # Load image
        if os.path.exists(image_path):
            try:
                img_clip = ImageClip(image_path)
                logger.info(f"Loaded image for scene {scene_num}")
            except Exception as e:
                logger.error(f"Failed to load image {image_path}: {e}", exc_info=True)

        if img_clip is None:
            logger.warning(f"Using black screen for scene {scene_num}")
            img_clip = ColorClip(size=video_size, color=(0, 0, 0)).set_duration(scene_duration)

        # Load audio
        if os.path.exists(audio_path):
            try:
                audio_clip = AudioFileClip(audio_path)
                scene_duration = max(audio_clip.duration, 0.1)
                logger.info(f"Loaded audio for scene {scene_num}")
            except Exception as e:
                logger.error(f"Failed to load audio {audio_path}: {e}", exc_info=True)
                audio_clip = None
        else:
            logger.warning(f"Audio not found for scene {scene_num}")

        # Resize image with aspect ratio preserved
        img_aspect = img_clip.w / img_clip.h
        target_aspect = target_width / target_height

        if img_aspect > target_aspect:
            # Wider than target: fit width, add top/bottom bars
            new_w = target_width
            new_h = int(target_width / img_aspect)
        else:
            # Taller than target: fit height, add side bars
            new_h = target_height
            new_w = int(target_height * img_aspect)

        img_clip = img_clip.resize(newsize=(new_w, new_h)).set_duration(scene_duration)
        img_clip = img_clip.set_position("center")

        # Create background and composite
        bg_clip = ColorClip(size=video_size, color=(0, 0, 0)).set_duration(scene_duration)
        final_clip = CompositeVideoClip([bg_clip, img_clip])

        if audio_clip:
            final_clip = final_clip.set_audio(audio_clip)

        clips.append(final_clip)
        logger.info(f"Scene {scene_num} added (duration: {scene_duration:.2f}s)")

    if not clips:
        logger.error("No valid clips found.")
        return None

    output_path = os.path.join(project_dir, output_filename)

    try:
        logger.info("Concatenating video...")
        final_video = concatenate_videoclips(clips, method="compose")

        logger.info(f"Exporting video to {output_path}...")
        final_video.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=os.path.join(project_dir, "temp_audio.m4a"),
            remove_temp=True,
            threads=4,
            preset='ultrafast',
            logger='bar'  # ✅ Enables default progress bar
        )

        logger.info(f"Video saved at {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Video generation failed: {e}", exc_info=True)
        return None

    finally:
        for clip in clips:
            try:
                clip.close()
                if clip.audio:
                    clip.audio.close()
            except Exception as e:
                logger.warning(f"Error closing clip: {e}")
        try:
            if 'final_video' in locals():
                final_video.close()
        except Exception as e:
            logger.warning(f"Error closing final video: {e}")
