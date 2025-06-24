# Joules V2 (Free Edition) - High-Level Architecture

## 1. Overall Philosophy

The Joules V2 (Free Edition) meeting tool is designed with a **local-first processing** approach as its core tenet. This prioritizes user privacy and control by keeping data on the user's machine wherever feasible. The architecture emphasizes **modular components**, allowing for flexibility and easier maintenance or upgrades. Finally, it relies heavily on **free and open-source software (FOSS)** to ensure accessibility and align with its "Free Edition" nature.

## 2. Core Components

The system is broken down into several key components:

### 2.1. Frontend (Client-Side)

*   **Responsibilities:**
    *   **Audio Recording:** Capturing audio input from the user's microphone.
    *   **User Interface (UI):** Providing a dashboard for meeting controls (start/stop recording, select processing options), displaying transcripts and summaries, and managing application settings.
    *   **Local Settings Management:** Storing user preferences (e.g., default language, preferred models) in the browser.
    *   **Client-Side Processing (Potential):** Performing transcription and/or summarization directly in the browser using WebAssembly (WASM) based models or by interacting with local helper applications.
*   **Technologies:**
    *   **Core:** HTML, CSS, JavaScript.
    *   **Frameworks (Optional):** Lightweight options like Preact or Svelte could be used for UI structure and reactivity. React is also an option if a more robust component model is preferred.
    *   **APIs:** WebRTC (specifically `navigator.mediaDevices.getUserMedia`) and the MediaRecorder API for audio capture.

### 2.2. Backend (Server-Side OR Local Orchestrator)

*   **Responsibilities:**
    *   **Audio Data Reception:** Receiving audio data from the frontend if it's not processed entirely client-side.
    *   **Transcription Orchestration:** Managing the transcription process, which could involve calling a local Whisper instance or a free-tier cloud API.
    *   **Summarization Orchestration:** Managing the summarization process. This primarily involves:
        *   Securely managing API key(s) for services like OpenRouter.ai.
        *   Formatting requests to the chosen summarization API (e.g., OpenRouter.ai) according to its specifications, including the transcript and any user-defined parameters (length, style).
        *   Handling responses from the summarization API, including error management (e.g., rate limits, API errors) and parsing the generated summary.
    *   **Meeting Metadata Management (Minimal):** Handling basic metadata if required (e.g., timestamps, meeting titles), though this is minimized in the local-first approach.
*   **Technologies:**
    *   **Primary:** Python (using Flask or FastAPI due to strong support for ML/AI libraries and rapid development) or Node.js (using Express.js for its asynchronous nature and JavaScript ecosystem).
    *   **Initial Implementation:** Can start as a simple local script that the user runs on their machine.

### 2.3. Transcription Module

*   **Responsibilities:** Converting spoken audio into written text.
*   **Technologies (Prioritized Order):**
    *   **Primary (Local):** OpenAI Whisper executed locally. This can be achieved via:
        *   The official `whisper` Python package.
        *   `whisper.cpp` for potentially higher performance and lower resource usage.
    *   **Alternative (Client-Side WASM):** In-browser Whisper implementations (e.g., `distil-whisper/whisper-web`). This offers a zero-backend setup but performance might be a constraint for longer audio or less powerful machines.
    *   **Fallback (Cloud-Based Free Tier):** Free-tier APIs for Whisper, such as:
        *   Hugging Face Inference API (for Whisper models).
        *   Replicate.
        *(User must be informed about data leaving their machine).*

### 2.4. Summarization Module

*   **Responsibilities:** Generating concise meeting notes, Minutes of Meeting (MOM), and extracting action items from the transcript.
*   **Technologies (Prioritized Order):**
    *   **Primary (Cloud-Based Free Tier):**
        *   **OpenRouter.ai:** Leverages its free-tier access to a variety of LLMs. The backend will manage interactions with OpenRouter. This is the default recommended approach for ease of use and access to capable models without requiring users to run local LLMs.
        *(User must be informed that the transcript (not audio) is sent to a third-party service for summarization).*
    *   **Alternative (Local - Advanced User Option):** Local LLMs running on the user's machine. This is positioned as an option for users who prefer full local processing and are willing to set up and manage local LLM servers.
        *   Tools like Ollama or LM Studio, providing interfaces to various open-source models (e.g., Mistral, LLaMA family).
        *   Direct integration with libraries like `llama.cpp` or `ctransformers`.
    *   **Fallback (Other Cloud-Based Free Tier):**
        *   Hugging Face Inference API (for suitable summarization models).
        *(User must be informed about data leaving their machine).*

### 2.5. Storage Module

*   **Responsibilities:** Persisting transcripts, summaries, and user preferences.
*   **Technologies (Prioritized Order):**
    *   **Primary (Local Browser):** Browser's LocalStorage or IndexedDB. Suitable for ephemeral data, user settings, or smaller amounts of text.
    *   **Alternative 1 (User-Initiated Local Save):** Standard "Save As" dialog functionality, allowing users to save files (e.g., `.txt`, `.md`) directly to their local file system. This is the simplest and most privacy-preserving persistent storage.
    *   **Alternative 2 (User-Controlled Cloud - Advanced/Optional):** Allow users to connect their own cloud storage (e.g., Google Drive, Dropbox). This typically involves client-side JavaScript libraries for direct interaction or backend integration using OAuth2. This adds significant complexity and is considered a future enhancement.
    *   **Alternative 3 (Free-Tier Cloud Database - Sparingly):** Services like Firebase Firestore (free tier) or Supabase (free tier). To be used cautiously due to free-tier limitations and potential privacy concerns if not managed by the user directly. Primarily for settings synchronization if a user opts-in.

## 3. Data Flow Scenarios

The data flow will depend on the chosen processing path, with a strong preference for local options.

### 3.1. Option A: Fully Client-Side (Ideal for Privacy & Simplicity)

1.  User clicks "Start Recording" in the browser frontend.
2.  Audio is captured using WebRTC/MediaRecorder, stored locally as a Blob or chunks.
3.  User clicks "Stop Recording."
4.  The audio Blob is processed by a WASM-based Whisper model running directly in the browser OR passed to a local helper application (e.g., a Python script the user has installed and is running).
5.  The local WASM model or helper app generates the transcript.
6.  The transcript is then fed into a WASM-based LLM in the browser or the same local helper application for summarization (if a suitable WASM LLM is available and performant). Alternatively, for summarization, the transcript might be sent to a backend (Option B or C style) if client-side summarization is not feasible.
7.  The resulting transcript and summary are displayed in the frontend UI.
8.  User can copy the text or use the "Save As" functionality (Storage Module - Alt 1) to save them as local files. LocalStorage might be used for temporary drafts.

### 3.2. Option B: Client + Lightweight Local Backend (Most Realistic MVP)

1.  User starts recording in the browser frontend.
2.  Audio is captured and stored locally (e.g., as a Blob).
3.  User stops recording.
4.  The audio Blob is sent from the frontend (e.g., via an HTTP POST request) to a locally running backend server (e.g., a Python Flask/FastAPI app listening on `http://localhost:PORT`).
5.  The local backend server uses a local Whisper instance (Python package or `whisper.cpp` subprocess) to transcribe the audio.
6.  The local backend server then sends the generated transcript to an external summarization service like **OpenRouter.ai** (managing API keys and formatting requests). Alternatively, if the user has configured it, the backend calls a local LLM instance (e.g., via Ollama).
7.  The transcript and summary are sent back to the frontend (e.g., as a JSON response to the HTTP request).
8.  Results are displayed in the UI. User can save locally via "Save As" or copy.

### 3.3. Option C: Client + Serverless/Managed Free-Tier Cloud Backend (Focus on Summarization via Cloud)

*This option describes a scenario where the backend itself might be a lightweight serverless function, or it refers to the part of any backend (local or remote) that interacts with cloud services. Privacy implications must be clearly communicated, especially for summarization.*

1.  User starts recording in the browser frontend. Audio is captured locally.
2.  User stops recording.
3.  Audio Blob is uploaded from the frontend to a backend (can be a local server as in Option B, or a serverless function if the entire backend is cloud-hosted).
4.  The backend calls a transcription service:
    *   Preferably a local Whisper instance if the backend is user-hosted (as in Option B).
    *   Optionally, a free-tier cloud Whisper API (e.g., Hugging Face) if the backend is serverless or the user opts for cloud transcription. (User consent needed).
5.  The transcription service returns the text to the backend.
6.  The backend then forwards the transcript to **OpenRouter.ai** for summarization. The backend manages the API key and interaction with OpenRouter.
7.  The summary is returned from OpenRouter.ai to the backend.
8.  The backend sends the transcript and summary back to the frontend.
9.  Results are displayed in the UI. User can save locally.

## 4. Key Interactions

*   **Frontend <-> Backend (if present, Options B & C):**
    *   Primarily RESTful API calls.
    *   `POST /transcribe` (with audio data) -> Returns job ID or direct transcript.
    *   `POST /summarize` (with transcript data) -> Returns summary.
    *   `GET /results/{job_id}` (if asynchronous processing).
*   **Backend <-> Transcription Module:**
    *   **Local (Option B):** Direct function call within the Python/Node.js application or execution of a subprocess (e.g., `whisper ...` or `main ...` from whisper.cpp).
    *   **Cloud (Option C):** HTTP API call to the chosen transcription service.
*   **Backend <-> Summarization Module:**
    *   **Primary (Option B & C):** HTTP API call from the backend to OpenRouter.ai.
    *   **Alternative (Local LLM, Option B advanced):** Direct function call, local HTTP call (to Ollama/LM Studio), or subprocess execution from the backend to a local LLM.
    *   **Cloud (Other fallback, Option C):** HTTP API call to another chosen LLM service (e.g., Hugging Face).

## 5. Modularity, Scalability, and Multi-User Mobile Vision

*   **Component Independence:** Each module (audio capture, UI, transcription, summarization, storage) is designed to be as independent as possible. Interfaces between them will be well-defined (e.g., API contracts, function signatures).
*   **Ease of Upgrades:** This modularity allows for swapping out implementations. For instance, a new summarization service can be integrated by updating the backend's interaction logic for that service.
*   **Scalability (User-Side & Service Limits):**
    *   "Scalability" for local processing primarily refers to handling larger audio files or longer meetings, managed by efficient local models and processing pipelines.
    *   For cloud services (like OpenRouter), scalability is handled by the provider, but free tiers will have usage limits (rate limits, quotas) that the backend must manage or make the user aware of.
*   **Architectural Considerations for Multi-User Mobile Vision:**
    *   **Backend Evolution:** The backend (whether user-hosted local server or a potential future cloud-hosted version) would need to evolve to manage multiple users, sessions, and potentially real-time communication.
    *   **Multiple Audio Streams:**
        *   Each mobile client participating in a multi-user session would likely send its audio stream (or chunks) to the backend.
        *   The backend would need a strategy for handling these streams:
            *   Process each stream separately for transcription and then attempt speaker diarization on the combined transcripts or use timing cues.
            *   Attempt to mix audio streams (if synchronized closely enough) and then perform transcription and diarization. This is more complex.
    *   **Speaker Diarization Module (Potential New Component):**
        *   *Responsibilities:* To identify and label different speakers within an audio stream or set of streams.
        *   *Technologies:* Could involve libraries like `pyannote.audio` (if run on the backend), or potentially a (hypothetical free-tier) cloud service specialized in diarization.
        *   *Integration Point:* Diarization could occur before transcription (by segmenting audio by speaker) or after transcription (by analyzing the transcript alongside audio cues). The former is often more effective if audio streams are separate.
    *   **Web Client for Link-Based Joining:**
        *   The architecture must support a lightweight web client, served by the backend or a static hosting service.
        *   This client would need capabilities for audio capture (WebRTC) and communication with the backend (e.g., WebSockets for real-time, or HTTP for chunked uploads).
    *   **User Identity Management (Lightweight):**
        *   For link-based joining in a multi-user session, a simple form of identity management would be needed.
        *   This could involve the backend issuing temporary participant IDs for a session, or clients storing a user-chosen name in `localStorage` to be sent with their audio contributions. More robust authentication would be needed for persistent user accounts (likely post-MVP).
    *   **Signaling Server (for WebRTC if direct P2P is too complex):** For coordinating connections between multiple clients, especially if not all are on the same network, a signaling mechanism (e.g., using WebSockets via the backend) might be necessary.

This architectural description provides a blueprint for developing Joules V2 (Free Edition) with a clear focus on its core principles and future evolution.
