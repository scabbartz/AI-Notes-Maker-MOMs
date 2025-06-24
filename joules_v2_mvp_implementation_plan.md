# Joules V2 (Free Edition) - MVP Implementation Plan

**Goal:** Create a functional web application that allows users to record audio in their browser, send it to a local backend for transcription using Whisper, and then get the transcript summarized using a local LLM (via Ollama) or a free-tier API.

**Core Philosophy for MVP:** Prioritize simplicity and local processing, aligning with "Option B (Client + Lightweight Local Backend)" from the architectural document. The user will run a local Python Flask server.

---

## **Step 1: Browser Audio Capture & Manual Download (Frontend Foundation)**

*   **Goal:** Allow users to record audio using their browser's microphone and then manually download the recorded audio as a file. This validates the core audio input mechanism.
*   **UI (HTML):**
    *   A "Record" button to start audio capture.
    *   A "Stop" button to end audio capture.
    *   A "Download Audio" button (initially disabled).
    *   An `<audio>` HTML element for playback of the recorded audio (optional but good for testing).
*   **Logic (JavaScript using `MediaRecorder` API):**
    1.  **Request Microphone Permission:** When the page loads or "Record" is clicked, request `navigator.mediaDevices.getUserMedia({ audio: true })`.
    2.  **Initialize `MediaRecorder`:** If permission is granted, create a new `MediaRecorder` instance with the obtained audio stream.
    3.  **Data Collection:**
        *   Attach an `ondataavailable` event listener to the `MediaRecorder`. When data is available (audio chunks), push it into an array (`audioChunks`).
    4.  **Start Recording:**
        *   When "Record" is clicked:
            *   Clear `audioChunks`.
            *   Call `mediaRecorder.start()`.
            *   Disable "Record" and "Download", enable "Stop".
    5.  **Stop Recording:**
        *   When "Stop" is clicked:
            *   Call `mediaRecorder.stop()`.
            *   The `mediaRecorder.onstop` event will fire. Inside this event handler:
                *   Create a `Blob` from the collected `audioChunks`. Specify a MIME type (e.g., `audio/wav` or `audio/webm`).
                *   Create an object URL for the `Blob` using `URL.createObjectURL()`.
                *   Set this URL as the `src` for the `<audio>` playback element.
                *   Enable "Download Audio" and "Record", disable "Stop".
    6.  **Download Audio:**
        *   When "Download Audio" is clicked:
            *   Create a temporary `<a>` element.
            *   Set its `href` to the object URL of the `audioBlob`.
            *   Set its `download` attribute to a desired filename (e.g., `meeting_audio.wav`).
            *   Programmatically click the `<a>` element to trigger the download.
            *   Remove the temporary `<a>` element.
*   **File Structure:**
    *   `index.html`
    *   `static/js/main.js` (optional, can be inline script in `index.html` for MVP)
*   **Code Snippet (HTML/JS - `index.html`):**
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JoulesV2 - MVP Audio Recorder</title>
        <style>
            body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
            button { padding: 10px 15px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
            #recordButton { background-color: #4CAF50; color: white; }
            #stopButton { background-color: #f44336; color: white; }
            #downloadButton { background-color: #008CBA; color: white; }
            audio { margin-top: 15px; }
        </style>
    </head>
    <body>
        <h1>JoulesV2 - MVP Audio Recorder</h1>
        <button id="recordButton">Record</button>
        <button id="stopButton" disabled>Stop</button>
        <br>
        <audio id="audioPlayback" controls></audio>
        <br>
        <button id="downloadButton" disabled>Download Audio</button>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let audioBlob;

            const recordButton = document.getElementById('recordButton');
            const stopButton = document.getElementById('stopButton');
            const downloadButton = document.getElementById('downloadButton');
            const audioPlayback = document.getElementById('audioPlayback');

            recordButton.onclick = async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' }); // Explicitly use webm for broader compatibility initially

                    mediaRecorder.ondataavailable = event => {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                        }
                    };

                    mediaRecorder.onstop = () => {
                        audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        audioChunks = []; // Reset for next recording
                        const audioUrl = URL.createObjectURL(audioBlob);
                        audioPlayback.src = audioUrl;
                        downloadButton.disabled = false;
                        recordButton.disabled = false;
                        stopButton.disabled = true;
                        // Clean up the stream tracks
                        stream.getTracks().forEach(track => track.stop());
                    };

                    mediaRecorder.start();
                    recordButton.disabled = true;
                    stopButton.disabled = false;
                    downloadButton.disabled = true;
                    audioPlayback.src = ''; // Clear previous playback
                } catch (err) {
                    console.error("Error accessing microphone:", err);
                    alert("Error accessing microphone. Please ensure permission is granted.");
                }
            };

            stopButton.onclick = () => {
                if (mediaRecorder && mediaRecorder.state === "recording") {
                    mediaRecorder.stop();
                }
            };

            downloadButton.onclick = () => {
                if (audioBlob) {
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(audioBlob);
                    a.download = 'meeting_audio.webm'; // Save as webm
                    document.body.appendChild(a);
                    a.click();
                    URL.revokeObjectURL(a.href); // Clean up
                    document.body.removeChild(a);
                }
            };
        </script>
    </body>
    </html>
    ```
*   **Testing:** Open `index.html` in a browser. Record, stop, playback, and download.

---

## **Step 2: Local Whisper Transcription Script (Backend Component 1)**

*   **Goal:** Create a standalone Python script that can take an audio file path as a command-line argument and print the transcript to standard output. This isolates the transcription logic.
*   **Technology:** Python, OpenAI's `whisper` library.
*   **Setup:**
    *   Ensure Python is installed.
    *   Install `whisper`: `pip install openai-whisper`
    *   (Whisper will download a model, e.g., "base", on first run if not already cached).
*   **Code Snippet (Python - `transcribe_script.py`):**
    ```python
    import whisper
    import sys
    import os

    def transcribe_audio(audio_file_path, model_size="base"):
        """
        Transcribes an audio file using OpenAI Whisper.
        """
        if not os.path.exists(audio_file_path):
            return f"Error: Audio file not found at {audio_file_path}"

        try:
            # Load the Whisper model (downloads if not present)
            # Consider making model loading more robust or a one-time setup for a server
            model = whisper.load_model(model_size)

            # Transcribe the audio file
            # fp16=False is recommended if not using NVIDIA GPU with CUDA support
            result = model.transcribe(audio_file_path, fp16=False)

            return result["text"]
        except Exception as e:
            return f"Error during transcription: {str(e)}"

    if __name__ == "__main__":
        if len(sys.argv) > 1:
            audio_path_arg = sys.argv[1]
            print(f"Transcribing {audio_path_arg} using '{MODEL_SIZE}' model...") # Using global MODEL_SIZE for clarity

            # Define MODEL_SIZE for the script execution context
            MODEL_SIZE = "base" # Default model for script execution

            transcript = transcribe_audio(audio_path_arg, model_size=MODEL_SIZE)
            print("\nTranscript:\n", transcript)
        else:
            print("Usage: python transcribe_script.py <path_to_audio_file> [model_size]")
            print("Example: python transcribe_script.py meeting_audio.webm base")
            print("Available models (typically): tiny, base, small, medium, large")
    ```
*   **Testing:**
    1.  Download an audio file from Step 1 (e.g., `meeting_audio.webm`).
    2.  Run the script from the terminal: `python transcribe_script.py meeting_audio.webm`
    3.  Verify that the transcript is printed to the console.

---

## **Step 3: Basic Frontend to Upload Audio and Display Transcript (Manual Flow)**

*   **Goal:** Modify the frontend to allow users to upload the audio file they recorded (or any compatible audio file). Still a manual process: user uploads, then *conceptually* runs the script, then pastes transcript. This step is about UI placeholders.
*   **UI (`index.html` changes):**
    *   Keep recording controls from Step 1.
    *   Add a file input: `<input type="file" id="audioUpload" accept="audio/*">`.
    *   Add a `<textarea id="transcriptOutput" placeholder="Transcript will appear here..." rows="10" cols="50"></textarea>`.
    *   Add a button: `<button id="processAudioButton">Process Audio (Manual)</button>`.
*   **Logic (JS - `index.html` or `static/js/main.js`):**
    *   When "Process Audio (Manual)" is clicked:
        *   Get the file from `audioUpload`.
        *   Display instructions to the user: "1. Save the recorded/uploaded audio. 2. Run `python transcribe_script.py <your_audio_file>` in your terminal. 3. Paste the transcript output here."
        *   (No actual processing yet, this is just UI setup for the flow).
*   **Testing:** Refresh `index.html`. Record/download or upload an audio file. See the instructions.

---

## **Step 4: Backend (Python/Flask) to Automate Transcription**

*   **Goal:** Create a simple Flask local web server that receives an audio file from the frontend, uses the `transcribe_audio` function from `transcribe_script.py` (or incorporates its logic), and returns the transcript as JSON.
*   **Technology:** Python, Flask.
*   **Setup:**
    *   `pip install Flask openai-whisper`
*   **Backend Logic (`app.py`):**
    ```python
    from flask import Flask, request, jsonify
    from flask_cors import CORS # For handling Cross-Origin Resource Sharing
    import whisper
    import os
    import tempfile

    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes, allowing requests from the frontend

    # It's better to load the model once when the server starts
    # For MVP, 'base' is fine. For more accuracy, 'small' or 'medium' could be used.
    MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")
    MODEL_LOAD_ERROR = None
    try:
        print(f"Loading Whisper model '{MODEL_SIZE}'...")
        model = whisper.load_model(MODEL_SIZE)
        print(f"Whisper model '{MODEL_SIZE}' loaded successfully.")
    except Exception as e:
        MODEL_LOAD_ERROR = f"Error loading Whisper model '{MODEL_SIZE}': {e}"
        print(MODEL_LOAD_ERROR)
        model = None # Ensure model is None if loading fails

    def transcribe_audio_file_from_upload(audio_file_path):
        if not model:
            return MODEL_LOAD_ERROR if MODEL_LOAD_ERROR else "Error: Whisper model not loaded."
        try:
            # fp16=False is generally safer unless specific GPU setup is confirmed
            result = model.transcribe(audio_file_path, fp16=False)
            return result["text"]
        except Exception as e:
            return f"Error during transcription: {e}"

    @app.route('/transcribe', methods=['POST'])
    def transcribe_endpoint():
        if model is None: # Check if model failed to load
             return jsonify({"error": MODEL_LOAD_ERROR}), 500

        if 'audio_file' not in request.files:
            return jsonify({"error": "No audio file part in the request"}), 400

        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file:
            # Use a temporary directory for saving the uploaded file
            temp_dir = tempfile.mkdtemp()
            # Sanitize filename or use a fixed name to avoid issues
            filename = "uploaded_audio.webm" # Or derive from file.filename safely
            temp_audio_path = os.path.join(temp_dir, filename)

            try:
                file.save(temp_audio_path)
                print(f"Audio file saved to {temp_audio_path}")
                transcript = transcribe_audio_file_from_upload(temp_audio_path)
            except Exception as e:
                print(f"Error saving or processing file: {e}")
                return jsonify({"error": f"Error saving or processing file: {e}"}), 500
            finally:
                # Clean up: remove the temporary file and directory
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                os.rmdir(temp_dir)

            if "Error:" in transcript: # Check for errors from transcription function
                 return jsonify({"error": transcript}), 500
            return jsonify({"transcript": transcript})
        else:
            # This case should ideally be caught by previous checks
            return jsonify({"error": "Unknown file error"}), 500

    if __name__ == '__main__':
        # Make sure to run on 0.0.0.0 to be accessible from browser if not on same machine (though for local dev, 127.0.0.1 is fine)
        # Port 5001 to avoid conflict with other common services
        app.run(debug=True, port=5001, host='127.0.0.1')
    ```
*   **Frontend Update (`index.html` or `static/js/main.js`):**
    *   Modify the "Process Audio (Manual)" button to "Transcribe Audio".
    *   When "Transcribe Audio" is clicked:
        1.  Get the `audioBlob` from recording (Step 1) or the file from `audioUpload`.
        2.  Create `FormData` and append the audio file/blob: `formData.append('audio_file', audioBlob, 'meeting_audio.webm');`
        3.  Use `fetch` to POST the `FormData` to `http://localhost:5001/transcribe`.
        4.  On success, get the JSON response, extract `response.transcript`, and display it in the `transcriptOutput` textarea.
        5.  Handle errors and display them to the user.
*   **Testing:**
    1.  Run `python app.py`. Ensure the Whisper model loads.
    2.  Open/refresh `index.html` in the browser.
    3.  Record audio or upload an audio file.
    4.  Click "Transcribe Audio".
    5.  Verify the transcript appears in the textarea. Check Flask console for logs.

---

## **Step 5: Summarization Pipeline (Transcript -> Prompt -> LLM)**

*   **Goal:** Create Python functions to take a transcript string and generate a summary using **OpenRouter.ai** as the primary service. Local LLMs (Ollama) will be an alternative/advanced option.
*   **Primary Technology:** OpenRouter.ai (leveraging its free-tier access to various LLMs).
    *   Users will need to sign up at [OpenRouter.ai](https://openrouter.ai/) to get an API key.
    *   The API key should be set as an environment variable (e.g., `OPENROUTER_API_KEY`).
*   **Alternative Technology (Advanced):** Local LLMs via Ollama.
*   **Code Snippet (Python - `summarize_utils.py`):**
    ```python
    import requests
    import json
    import os

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    # Recommended: Check OpenRouter documentation for current free/low-cost models.
    # Using a commonly available model like Mistral 7B Instruct as an example.
    # Other options could be "nousresearch/nous-capybara-7b-v1.9" or "gryphe/gryphe-mistral-7b-instruct-v0.1"
    # Always verify model availability and pricing/rate limits on OpenRouter.
    DEFAULT_OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")


    def summarize_with_openrouter(transcript_text, model_name=DEFAULT_OPENROUTER_MODEL):
        """
        Summarizes a transcript using a model via OpenRouter.ai.
        """
        if not OPENROUTER_API_KEY:
            return "Error: OPENROUTER_API_KEY environment variable not set."

        # Using a prompt from joules_v2_prompt_engineering_guidelines.md (Basic Concise Summary)
        # For more complex summaries, use other prompts or allow prompt selection.
        prompt_template = """Please provide a concise summary of the following meeting transcript. Focus on the main topics discussed and key outcomes.

Transcript:
\"\"\"
{transcript}
\"\"\"

Concise Summary:"""

        formatted_prompt = prompt_template.format(transcript=transcript_text)

        try:
            response = requests.post(
                url=OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": formatted_prompt}
                    ]
                }
            )
            response.raise_for_status()  # Raises an exception for HTTP errors
            api_response = response.json()

            if api_response.get("choices") and len(api_response["choices"]) > 0:
                summary = api_response["choices"][0].get("message", {}).get("content", "")
                if summary:
                    return summary.strip()
                else:
                    return f"Error: Empty summary content in OpenRouter response. Full response: {api_response}"
            else:
                return f"Error: Unexpected OpenRouter API response structure. Full response: {api_response}"

        except requests.exceptions.RequestException as e:
            return f"Error connecting to OpenRouter API: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    # Ollama function can be kept as an alternative for advanced users
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    def summarize_with_ollama(transcript, model_name="mistral"):
        # (Ollama implementation from original plan can remain here)
        # Basic prompt, can be refined.
        prompt = f"""Please provide a concise summary of the key discussion points, decisions, and action items from the following meeting transcript.
        If there are no clear action items, state that.

        Transcript:
        "{transcript}"

        Summary:
        """
        payload = {"model": model_name, "prompt": prompt, "stream": False}
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
            response.raise_for_status()
            summary = response.json().get("response", "Error: 'response' field not found.")
            return summary.strip()
        except Exception as e:
            return f"Error with Ollama: {e}"


    if __name__ == "__main__":
        sample_transcript = """
        Alice said this is a very important meeting. We need to decide on the new project management tool.
        Bob proposed using ToolMaster Pro because of its advanced features and reporting capabilities.
        Carol mentioned that ToolMaster Pro might be too expensive and suggested looking into FreePlan, which is open source.
        Alice asked Bob to prepare a cost-benefit analysis for ToolMaster Pro by next Monday.
        Carol agreed to research FreePlan's features and present them in the next meeting.
        David: I think we should also consider how easy it is to integrate with our current systems.
        Alice: Good point David. Bob, Carol, please include integration aspects in your reports. Action for Bob: Cost-benefit for ToolMaster Pro by Monday. Action for Carol: Feature review of FreePlan by next meeting.
        """

        print("Attempting summarization with OpenRouter.ai...")
        if not OPENROUTER_API_KEY:
            print("Skipping OpenRouter test as OPENROUTER_API_KEY is not set.")
        else:
            openrouter_summary = summarize_with_openrouter(sample_transcript)
            print("\nOpenRouter.ai Summary:\n", openrouter_summary)

        print("\nAttempting summarization with Ollama (mistral)...")
        # Ensure Ollama is running and 'mistral' model is pulled: `ollama run mistral`
        # This part will only work if Ollama is set up and running
        try:
            ollama_summary = summarize_with_ollama(sample_transcript)
            print("\nOllama Summary:\n", ollama_summary)
        except Exception as e:
            print(f"Could not connect to Ollama or Ollama not set up: {e}")

    ```
*   **Testing:**
    1.  Set your `OPENROUTER_API_KEY` environment variable.
    2.  (Optional) Ensure Ollama is running (`ollama serve`) and you have a model like `mistral` available if you want to test the Ollama path.
    3.  Run `python summarize_utils.py` from the terminal.
    4.  Verify that a summary is printed from OpenRouter.ai.

---

## **Step 6: Integrate Summarization into the Backend**

*   **Goal:** Add a new `/summarize` endpoint to the Flask app. This endpoint will accept a transcript (as JSON), call the `summarize_with_openrouter` function, and return the summary.
*   **Backend Logic (`app.py` update):**
    ```python
    # ... (previous Flask app code for /transcribe, model loading etc.) ...
    # Import the summarization functions
    from summarize_utils import summarize_with_openrouter, summarize_with_ollama

    # Configuration for summarizer choice
    # For MVP, OpenRouter is the default. Ollama can be an advanced option if user configures it.
    DEFAULT_SUMMARIZER = os.getenv("DEFAULT_SUMMARIZER", "openrouter")
    OPENROUTER_MODEL_NAME = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")


    @app.route('/summarize', methods=['POST'])
    def summarize_endpoint():
        data = request.get_json()
        if not data or 'transcript' not in data:
            return jsonify({"error": "Missing 'transcript' in request body"}), 400

        transcript = data['transcript']
        if not transcript.strip():
            return jsonify({"error": "Transcript cannot be empty"}), 400

        # For MVP, we'll primarily use OpenRouter.
        # The 'summarizer_choice' could be used later for more advanced user settings.
        # summarizer_choice = data.get("summarizer", DEFAULT_SUMMARIZER).lower()
        summary = ""

        print(f"Summarization request received. Using OpenRouter with model {OPENROUTER_MODEL_NAME}")
        summary = summarize_with_openrouter(transcript, model_name=OPENROUTER_MODEL_NAME)

        # Example of how to allow Ollama as an alternative if specified (more advanced)
        # if summarizer_choice == "ollama":
        #     print(f"Summarization request received. Using Ollama with model {OLLAMA_MODEL_NAME}")
        #     summary = summarize_with_ollama(transcript, model_name=OLLAMA_MODEL_NAME)
        # elif summarizer_choice == "openrouter":
        #     print(f"Summarization request received. Using OpenRouter with model {OPENROUTER_MODEL_NAME}")
        #     summary = summarize_with_openrouter(transcript, model_name=OPENROUTER_MODEL_NAME)
        # else:
        #     return jsonify({"error": f"Invalid summarizer choice: {summarizer_choice}."}), 400

        if "Error:" in summary: # Convention from summarize_utils
            # More specific error checking might be needed depending on actual error messages
            return jsonify({"error": summary}), 500

        return jsonify({"summary": summary})

    # ... (rest of app.py, including if __name__ == '__main__': block)
    ```
*   **Frontend Update (`index.html` or `static/js/main.js`):**
    *   Add a `<textarea id="summaryOutput" placeholder="Summary will appear here..." rows="10" cols="50"></textarea>`.
    *   Add a "Summarize Transcript" button (e.g., `<button id="summarizeButton">Summarize</button>`).
    *   After a transcript is successfully fetched and displayed:
        *   Enable the "Summarize" button.
        *   When "Summarize" is clicked:
            1.  Get the transcript text from `transcriptOutput`.
            2.  Use `fetch` to POST JSON `{"transcript": transcript_text}` to `http://localhost:5001/summarize`. (Optionally add a way to select 'ollama' or 'hf').
            3.  On success, display the `response.summary` in `summaryOutput`.
            4.  Handle errors.
*   **Testing:**
    1.  Restart `python app.py`.
    2.  In `index.html`: Record/upload audio -> Transcribe.
    3.  Once transcript appears, click "Summarize".
    4.  Verify summary appears. Check Flask console for logs about which summarizer was used.

---

## **Step 7: Develop a Simple Dashboard UI**

*   **Goal:** Improve the UI to be more user-friendly. This involves organizing controls and display areas. For MVP, "dashboard" means a single, well-organized page.
*   **UI (`index.html` enhancements):**
    *   **Layout:** Use simple CSS (or a micro-framework like Pico.css for nicer defaults) for better structure.
        *   Section for Recording: Record, Stop buttons. Audio playback.
        *   Section for Processing: Upload button (alternative to recording), Transcribe button.
        *   Section for Results:
            *   Textarea for Transcript (read-only after population).
            *   Button to trigger Summarization.
            *   Textarea for Summary (read-only after population).
            *   Button to "Save All Results" (JS to compile transcript + summary into a text string and trigger download of a `.txt` or `.md` file).
    *   **Visual Feedback:** Add loading indicators (e.g., "Transcribing...", "Summarizing...") during backend calls.
    *   **Error Display:** A dedicated area or alert pop-ups for errors from backend or JS.
*   **Logic (JS - `static/js/main.js`):**
    *   Refactor JS into functions for clarity (e.g., `handleRecord`, `handleStop`, `handleTranscribe`, `handleSummarize`, `handleSave`).
    *   Manage UI state (enable/disable buttons appropriately based on current state - e.g., don't allow summarize if no transcript).
    *   "Save All Results" function:
        ```javascript
        function saveResults() {
            const transcript = document.getElementById('transcriptOutput').value;
            const summary = document.getElementById('summaryOutput').value;
            if (!transcript && !summary) {
                alert("Nothing to save!");
                return;
            }
            const fullText = `## Meeting Transcript\n\n${transcript}\n\n## Meeting Summary\n\n${summary}`;
            const blob = new Blob([fullText], { type: 'text/markdown;charset=utf-8' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'meeting_notes.md';
            document.body.appendChild(a);
            a.click();
            URL.revokeObjectURL(a.href);
            document.body.removeChild(a);
        }
        // Attach to a "Save Results" button.
        ```
*   **Testing:** Thoroughly test all UI interactions, error states, and the save functionality.

---

## **Step 8: (Optional for MVP, More for Planning) Outline Calendar Integration Ideas**

*   **Goal:** Briefly describe how fetching meeting titles for annotation could work, acknowledging it's likely post-MVP.
*   **Concept:**
    1.  **Authentication:** User would need to authenticate with their calendar provider (e.g., Google Calendar via OAuth 2.0). This is a significant piece of work.
    2.  **API Interaction (Client-Side for Google):**
        *   Use Google API JavaScript Client Library.
        *   Request `calendar.readonly` scope.
        *   Fetch upcoming or recent calendar events.
    3.  **UI Integration:**
        *   Allow user to select a meeting from their calendar.
        *   Use the meeting title/details to pre-fill information or tag the recording.
*   **Notes for MVP:**
    *   This adds considerable complexity (OAuth, API client libraries, UI for event selection).
    *   For MVP, users can manually name their saved files or copy-paste titles.
    *   This step is primarily for future roadmap consideration.

---

## **General MVP Considerations & Next Steps:**

*   **Error Handling:** Improve user-facing error messages throughout the application. Provide clear feedback if the backend isn't running or if models fail to load.
*   **Styling:** Apply basic CSS to make the application presentable.
*   **User Instructions:** Create a `README.md` with:
    *   Prerequisites (Python, pip, browser).
    *   How to install dependencies (`pip install -r requirements.txt`).
    *   **Crucially:** How to sign up for OpenRouter.ai, get an API key, and set it as the `OPENROUTER_API_KEY` environment variable.
    *   (Optional) Instructions for setting up Ollama if users want to use local LLMs.
    *   How to run the Flask backend (`python app.py`).
    *   How to use the web application (open `index.html`).
    *   Notes on model downloading (Whisper on first run).
    *   Environment variables (`OPENROUTER_API_KEY`, `WHISPER_MODEL`, `OPENROUTER_MODEL` (optional), `OLLAMA_API_URL` (optional), `OLLAMA_MODEL` (optional)).
*   **`requirements.txt`:**
    ```
    Flask
    flask-cors
    openai-whisper
    requests
    ```
*   **Configuration:** Encourage use of environment variables for API keys, model names, etc.
*   **Packaging/Distribution (Post-MVP):** Think about how a non-technical user might eventually use this (e.g., PyInstaller for backend, or simple zip for frontend if backend is hosted elsewhere). For MVP, running `python app.py` and opening `index.html` is sufficient.

This detailed plan provides a structured path to building the MVP for Joules V2 (Free Edition). Each step builds upon the previous one, focusing on delivering a functional core experience first.
