# Story2Scene AI Video Generator

This project is an AI Video Generator that transforms creative text prompts into captivating videos by generating stories, images, and audio, then synchronizing them into a final video.

## ✨ Features

* **AI-Powered Story Generation:** Converts user prompts into structured stories using OpenAI's GPT models.
* **Dynamic Image Creation:** Generates corresponding visual scenes using DALL-E, with an optional feature to use a base image for character consistency.
* **Narrated Audio:** Creates natural-sounding narration for each scene using Text-to-Speech (TTS).
* **Seamless Video Synchronization:** Combines generated images and audio into a complete video using MoviePy.
* **Web-Based User Interface:** Provides an intuitive web application for easy interaction.
* **Video Playback & Download:** Allows users to preview and download the generated videos directly from the browser.

##  Getting Started

Follow these steps to set up and run the Story2Scene AI Video Generator on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.9+** (or a compatible version)
* **pip** (Python package installer)
* **FFmpeg**: This is crucial for MoviePy to handle video processing.
    * **Windows:** Download the FFmpeg executable from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system's PATH environment variable.
    * **macOS:** `brew install ffmpeg` (if using Homebrew)
    * **Linux:** `sudo apt-get install ffmpeg` (for Debian/Ubuntu)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Chandu1234545/Story2Scene.git](https://github.com/Chandu1234545/Story2Scene.git)
    cd Story2Scene
    ```
    *(**IMPORTANT:** Replace `your-username` with your actual GitHub username)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv storyenv
    # On Windows:
    .\storyenv\Scripts\activate
    # On macOS/Linux:
    source storyenv/bin/activate
    ```

3.  **Install dependencies:**
    First, ensure you have a `requirements.txt` file in your project root. If not, you can generate one from your installed packages:
    ```bash
    pip freeze > requirements.txt
    ```
    Then, install:
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure `moviepy`, `openai`, `python-dotenv`, `flask`, `Pillow`, `requests` are listed in your `requirements.txt`)*

4.  **Set up OpenAI API Key:**
    You will need an OpenAI API key to use the AI generation services (story, image, and audio).
    * Create a file named `.env` in the root directory of your project (the same level as `app.py`).
    * Add your OpenAI API key to this file:
        ```
        OPENAI_API_KEY="your_openai_api_key_here"
        ```
    **Important:** OpenAI API keys operate on a usage-based pricing model. If you encounter "quota exceeded" errors (Error code: 429), it means your API key has run out of credits or hit a spending limit. You will need to check your OpenAI billing details at [https://platform.openai.com/](https://platform.openai.com/) and add more funds if necessary.

## 💡 Usage

1.  **Start the Flask server:**
    Ensure your virtual environment is activated, then run:
    ```bash
    python app.py
    ```
    The server will typically start on `http://127.0.0.1:5000/`. A browser window should automatically open.

2.  **Access the web application:**
    Open your web browser and navigate to `http://127.0.0.1:5000/`.

3.  **Generate your video:**
    * Enter your desired **Story Prompt**.
    * Choose the **Number of Scenes** (1-10).
    * Select a **Story Style**.
    * *(Optional)* Upload a **Base Image** if you want the AI image generation to reference an existing character or style for consistency.
    * Click the "Generate Video" button.

4.  **View and Download:**
    Once the generation is complete, the video will appear on the page for playback. You can also click "Download Video" to save it to your local machine.

## 📁 Project Structure
Story2Scene/
├── app.py                      # Main Flask application, routes, and orchestration of AI services
├── story_generation.py         # Handles AI story generation (GPT models)
├── image_generation.py         # Manages DALL-E image generation and variations
├── audio_generation.py         # Handles Text-to-Speech (TTS) audio generation
├── video_synchronization.py    # Combines images and audio into a final video using MoviePy
├── index.html                  # Frontend HTML for the user interface
├── static/
│   └── styles.css              # CSS for styling the frontend
├── generated_videos/           # Directory to store all generated assets (videos, images, audio)
│   └── temp_uploads/           # Temporary storage for uploaded base images
│   └── [YOUR_STORY_TITLE_TIMESTAMP]/ # Subdirectory for each video project's assets
│       ├── scene_1.jpg
│       ├── scene_1.mp3
│       └── final_video.mp4
├── .env                        # Environment variables (e.g., OPENAI_API_KEY - DO NOT COMMIT!)
├── requirements.txt            # Python dependencies
└── README.md                   # This file!


## ⚠️ Troubleshooting

* **`Error code: 429 - You exceeded your current quota`**: This is a billing error from OpenAI. Your API key has insufficient funds or has reached a spending limit. Please check your OpenAI billing dashboard at [https://platform.openai.com/](https://platform.openai.com/) to resolve this.
* **Missing Video/Audio/Images in Output**:
    * Check your Flask server's console for any `ERROR` or `WARNING` messages from `audio_generation.py`, `image_generation.py`, or `video_synchronization.py`.
    * Verify that `*.mp3` and `*.jpg` files are actually being created inside the `generated_videos/[YOUR_STORY_TITLE_TIMESTAMP]` subdirectories after a generation attempt.
    * Ensure FFmpeg is correctly installed and accessible in your system's PATH.
* **Frontend Issues (e.g., UI not loading correctly)**:
    * Perform a hard refresh in your browser (`Ctrl+F5` or `Cmd+Shift+R`).
    * Check the browser's developer console (F12) for any JavaScript errors.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or find any issues, please open an issue or submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---
