# Joules V2 (Free Edition) - Meeting Recorder, Transcriber, and Summarizer

**Record your meetings, get transcripts, and generate summaries/notes – all for free, with a focus on privacy and using free-tier APIs.**

## Overview

Joules V2 (Free Edition) is an open-source web-based tool designed to help you get more out of your meetings. It allows you to:

*   **Record Audio:** Capture meeting audio directly in your browser.
*   **Upload Audio:** Process existing audio files.
*   **Transcribe Audio:** Convert spoken words into text using OpenAI's Whisper model run locally via a Python backend.
*   **Summarize & Generate Notes:** Use free-tier Large Language Models (LLMs) via OpenRouter.ai to create concise summaries from your transcripts.

**Core Principles:**
*   **Free & Open Source:** Built with free and open-source components and services.
*   **Privacy Aware:** Local transcription by default. Summarization uses external APIs, and users should be aware of the terms of those services.
*   **Cost-Effective:** Aims for zero to minimal operational costs for users by leveraging local processing and free API tiers.
*   **Modular & Extensible:** Designed to be easy to understand, modify, and extend.

## Features (Implemented MVP)

*   In-browser audio recording (using MediaRecorder API, saves as WEBM).
*   Local audio file upload.
*   Automated transcription via a local Python/Flask backend using OpenAI Whisper (default model: "base").
*   Automated summarization by sending the transcript to the backend, which then calls OpenRouter.ai (default model: "mistralai/mistral-7b-instruct:free").
*   Display of transcript and generated summary.
*   Simple client-side dashboard (using `localStorage`) to:
    *   Save processed meetings (name, transcript, summary, timestamp).
    *   View a list of saved meetings.
    *   Load and display the transcript/summary of a saved meeting.
    *   Delete individual meetings or clear the entire history.

## Tech Stack (MVP)

*   **Frontend:** HTML, CSS, JavaScript (ES6+)
    *   No complex JS framework used for this MVP to keep it lightweight.
*   **Backend (Local Server):** Python with Flask
    *   Serves `/transcribe` and `/summarize` endpoints.
    *   Uses `Flask-CORS` for cross-origin requests from the frontend.
*   **Transcription:** `openai-whisper` Python package (running locally via the Flask backend).
*   **Summarization:** Calls to **OpenRouter.ai API** (using models like Mistral 7B Instruct on their free tier).
*   **Local Storage:** Browser `localStorage` for the client-side meeting history dashboard.

## Getting Started / Setup Instructions

**Prerequisites:**

*   **Python 3.8+** and `pip` (Python package installer).
*   **`ffmpeg`:** OpenAI Whisper requires `ffmpeg` to be installed on your system and available in your PATH. You can download it from [ffmpeg.org](https://ffmpeg.org/download.html).
*   **OpenRouter.ai API Key:**
    1.  Sign up at [OpenRouter.ai](https://openrouter.ai/).
    2.  Obtain your API key from your OpenRouter account page.
    3.  You will need to set this API key as an environment variable named `OPENROUTER_API_KEY` for the backend to use it. How to set environment variables depends on your OS:
        *   **Linux/macOS (temporary for current session):** `export OPENROUTER_API_KEY='your_api_key_here'` in your terminal before running the backend.
        *   **Windows (temporary for current session):** `set OPENROUTER_API_KEY=your_api_key_here` in your command prompt.
        *   (For persistent setup, add it to your shell profile like `.bashrc`, `.zshrc`, or System Environment Variables on Windows).

**1. Clone the Repository (if you haven't already):**

```bash
# If you are developing this project, you likely have it already.
# For a new user:
# git clone https://github.com/your-username/joules-v2-free-edition.git
# cd joules-v2-free-edition
```

**2. Setup Backend & Dependencies:**

Navigate to the `backend` directory:
```bash
cd backend
```

Create a virtual environment (recommended):
```bash
python -m venv venv
```

Activate the virtual environment:
*   Linux/macOS: `source venv/bin/activate`
*   Windows: `venv\Scripts\activate`

Install Python dependencies:
```bash
pip install -r requirements.txt
```

**3. Set `OPENROUTER_API_KEY` Environment Variable:**

Make sure you have set your `OPENROUTER_API_KEY` in your terminal session as described in the Prerequisites.

**4. Run the Backend Server:**

From the `backend` directory (with the virtual environment activated):
```bash
python app.py
```
You should see output indicating the Flask server is running, typically on `http://localhost:5001` or `http://0.0.0.0:5001`.

**5. Run the Frontend:**

Open the `frontend/index.html` file directly in your web browser.
*   Navigate to the `frontend` directory in your file explorer.
*   Double-click `index.html` or right-click and choose "Open with" your preferred browser.

**6. Using the Application:**

*   Once the backend is running and `frontend/index.html` is open in your browser:
    *   Grant microphone permission if prompted when you click "Record New Meeting".
    *   Record audio or upload an audio file.
    *   Click "Process Audio (Transcribe & Summarize)".
    *   Wait for processing (transcription can take time depending on audio length and your CPU; summarization depends on API response time).
    *   View the transcript and summary.
    *   Optionally, save the meeting to your dashboard using a name you provide.
    *   Manage saved meetings in the "Meeting History" panel.

## Further Documentation

This project was initially planned with a comprehensive set of design documents. While not included directly in this repository's root, these documents cover:

*   `joules_v2_architecture.md`: System architecture.
*   `joules_v2_mvp_implementation_plan.md`: Original detailed plan for this MVP.
*   `joules_v2_prompt_engineering_guidelines.md`: Tips for summarization prompts.
*   `joules_v2_tooling_and_services.md`: List of considered tools and services.
*   `joules_v2_mobile_extension_strategy.md`: Planning for a future mobile application.
*   `joules_v2_performance_privacy_fallbacks.md`: Notes on performance, privacy, and errors.

(These would typically reside in a `/docs` folder in a larger project setup.)

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

(A more formal `CONTRIBUTING.md` would be beneficial for larger projects.)

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for details (if one is added - for now, assume MIT).

## Acknowledgements

*   OpenAI for the Whisper model.
*   OpenRouter.ai for providing access to various LLMs.
*   The Flask and broader Python open-source communities.
```
