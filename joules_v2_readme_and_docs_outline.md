# Joules V2 (Free Edition) - README Skeleton and Developer Documentation Outline

This document provides a skeleton for the main `README.md` file and an outline for the comprehensive developer documentation for the Joules V2 (Free Edition) project.

## README.md Skeleton

```markdown
# Joules V2 (Free Edition) - Meeting Recorder, Transcriber, and Summarizer

**Record your meetings, get transcripts, and generate summaries/notes – all for free, with a strong focus on privacy and local processing.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other relevant badges: build status, version, etc. -->
<!-- [Link to Live Demo/PWA (if applicable/deployed)] | [Link to Project Board (if any)] | [Link to Contribution Guidelines] -->

## Overview

Joules V2 (Free Edition) is an open-source, web-based tool designed to help you capture, understand, and extract value from your meetings. It allows you to:

*   **Record Audio:** Securely capture meeting audio directly in your browser.
*   **Transcribe Audio:** Convert spoken words into accurate text using state-of-the-art speech recognition (primarily leveraging OpenAI's Whisper).
*   **Summarize & Generate Notes:** Utilize Large Language Models (LLMs) to create concise summaries, extract key discussion points, and identify action items from your transcripts.

**Core Principles:**

*   **Free & Open Source:** Built entirely with freely available and open-source components. We believe in community-driven development.
*   **Privacy First:** Prioritizes local processing. By default, your audio and meeting data stay on your machine, ensuring confidentiality.
*   **Cost-Effective:** Aims for zero to minimal operational costs for end-users.
*   **Modular & Extensible:** Designed with a clear architecture to be easy to understand, modify, and extend by contributors.

## Features (MVP)

*   In-browser audio recording using the `MediaRecorder` API.
*   Option to upload existing local audio files (e.g., `.wav`, `.mp3`, `.webm`).
*   Transcription using locally run instances of OpenAI Whisper (via Python backend or `whisper.cpp` for efficiency).
    *   User-selectable Whisper model size (e.g., `tiny`, `base`, `small`) to balance speed and accuracy, especially for CPU users.
*   Summarization using **OpenRouter.ai** (free-tier LLMs) via backend.
    *   Optional: Support for local LLMs (e.g., via Ollama) for summarization if configured by the user.
*   Clear display of generated transcript and summary/notes.
*   Functionality to download the transcript and summary (e.g., as `.txt` or `.md` files).
*   Simple interface to manage and view recently processed meetings (data stored locally in the browser or managed via downloaded files).

## Tech Stack (Primary for Local-First MVP)

*   **Frontend:** HTML, CSS, JavaScript (Potentially with a lightweight framework like Preact/Svelte, or plain JS for maximum simplicity. Vite for bundling and development server).
*   **Backend (Local Server):** Python (using Flask or FastAPI for orchestration).
*   **Transcription Engine:** OpenAI Whisper (Python package or `whisper.cpp` running locally on the user's machine).
*   **Summarization Engine (Default):** **OpenRouter.ai** (free-tier access to various models) called by the backend.
*   **Alternative Summarization (Local):** Ollama (running models like Mistral, LLaMA locally) for advanced users or full offline preference.

## Getting Started / Setup Instructions

**(This section will provide clear, step-by-step instructions to get a local instance of Joules V2 running.)**

**Prerequisites:**

*   Python 3.8+
*   `pip` (Python package installer)
*   A modern web browser (e.g., Chrome, Firefox, Edge).
*   **(Highly Recommended for Local Summarization)** [Ollama](https://ollama.com/) installed, and at least one model pulled (e.g., `ollama pull mistral`).
*   **(Optional, for `whisper.cpp` users)** A C++ compiler and Make tools (specific instructions will be in the detailed setup).
*   **(Optional, for GPU acceleration with Whisper Python package)** An NVIDIA GPU, CUDA Toolkit, and cuDNN installed and configured.

**1. Clone the Repository:**

```bash
git clone https://github.com/your-username/joules-v2-free-edition.git
cd joules-v2-free-edition
```

**2. Setup Backend & Dependencies:**

```bash
# Navigate to the backend directory (e.g., backend/)
cd backend/

# Create a Python virtual environment (recommended)
python -m venv venv
# Activate the virtual environment:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Initial Whisper model download may occur on first run of the backend,
# or provide specific instructions here if manual download is preferred.
# e.g., Python -c "import whisper; whisper.load_model('base')"
```

**3. Configure Local Services (if applicable):**

*   **Ollama:**
    *   Ensure your Ollama application is running if you intend to use it for summarization.
    *   Verify you have pulled a model: `ollama list` (if not, `ollama pull mistral` or another preferred model).
*   **Whisper.cpp:** (If this path is chosen, detailed compilation and model download instructions will be in `docs/detailed_setup.md`).

**4. Run the Backend Server:**

```bash
# From the backend directory (ensure virtual environment is active)
python app.py  # Or your main backend script (e.g., main.py for FastAPI)
# Expected output: Server running on http://localhost:5001 (or similar port as configured)
```

**5. Run the Frontend:**

*   **Option A (Simple HTML/JS - No Build Step):**
    *   Navigate to the `frontend/` directory (e.g., `cd ../frontend/`).
    *   Open the `index.html` file directly in your web browser.
*   **Option B (If using a JS framework with a build step like Vite):**
    ```bash
    # Navigate to the frontend directory (e.g., frontend/)
    cd ../frontend/
    npm install # or yarn install (if package-lock.json/yarn.lock exists)
    npm run dev # or yarn dev
    # Expected output: Frontend development server running on http://localhost:3000 (or similar)
    ```

**6. Using the Application:**

*   Open the frontend URL (e.g., `index.html` or `http://localhost:3000`) in your browser.
*   Use the "Record" button to capture new audio, or use the "Upload" button for an existing audio file.
*   Wait for the transcription and summarization processes to complete. Progress should be indicated.
*   View the generated transcript and summary.
*   Use the "Download" buttons to save your results.

## Developer Documentation

For more detailed information on the project's architecture, setup, development processes, and contribution guidelines, please refer to our Developer Documentation located in the `/docs` directory or our project Wiki (link if applicable).

**Key Documents:**
*   [Architecture Overview](docs/architecture.md)
*   [Detailed Setup Guide](docs/detailed_setup.md)
*   [Frontend Development Guide](docs/frontend_development.md)
*   [Backend Development Guide](docs/backend_development.md)
*   [Prompt Engineering Guidelines](docs/prompt_engineering_guidelines.md)

*(A full list is in the Developer Documentation Outline section below)*

## Contributing

We warmly welcome contributions from the community! If you're interested in helping improve Joules V2, please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to get started, our coding standards, and the pull request process.

## License

This project is licensed under the [MIT License](LICENSE.md) (or specify another chosen open-source license like Apache 2.0).

## Acknowledgements

*   The OpenAI team for the Whisper model.
*   The Ollama team for making local LLM hosting accessible.
*   The developers and communities behind the various open-source LLMs and libraries that make this project possible.
*   All community contributors who help shape and improve Joules V2.

---
```

## Developer Documentation Outline

This outline details the structure and content for the comprehensive developer documentation, likely to be housed in a `/docs` directory within the repository or on a project Wiki. The previously generated markdown files will serve as foundational content for these sections.

1.  **Introduction & Project Goals**
    *   (Briefly covered in README, can be expanded here with vision and scope)
2.  **Architecture Overview (`docs/architecture.md`)**
    *   Based on `joules_v2_architecture.md`.
    *   High-level component diagram (visual).
    *   Detailed description of Frontend, Backend, Transcription, Summarization, and Storage modules.
    *   Data flow diagrams for different processing scenarios (local-only, cloud-assisted fallback).
    *   Rationale behind key technology choices.
3.  **Detailed Setup Guide (`docs/detailed_setup.md`)**
    *   Comprehensive environment setup for various OS (Windows, macOS, Linux).
    *   In-depth instructions for installing and configuring Whisper (Python package, `whisper.cpp`), including GPU acceleration (CUDA, Metal).
    *   Detailed steps for installing, configuring, and managing local LLM servers (Ollama, LM Studio, or direct Python libraries), including model downloading and management.
    *   Instructions for obtaining and configuring API keys for optional free-tier cloud services (Hugging Face, OpenRouter, etc.), emphasizing secure storage of keys.
4.  **Frontend Development (`docs/frontend_development.md`)**
    *   Detailed breakdown of the `frontend/` directory structure.
    *   In-depth explanation of key UI components, their responsibilities, and interactions.
    *   State management strategy (e.g., context API, signals, simple event-driven state).
    *   Detailed guide on API interaction with the backend (request/response formats, error handling).
    *   Instructions for building the frontend for production and deployment strategies for static sites.
5.  **Backend Development (`docs/backend_development.md`)**
    *   Detailed breakdown of the `backend/` directory structure.
    *   Comprehensive API endpoint documentation (routes, HTTP methods, request parameters, response formats, status codes).
    *   Deep dive into the integration with the Whisper module (how audio is passed, how results are retrieved).
    *   Deep dive into the integration with the LLM summarization module (prompt construction, context handling, API calls to local/remote LLMs).
    *   Strategies for error handling, logging, and debugging in the backend.
    *   Managing dependencies and virtual environments.
6.  **Transcription Module (`docs/transcription_module.md`)**
    *   Advanced usage of the Whisper library or `whisper.cpp`.
    *   Guidance on managing different Whisper model sizes (downloading, selection logic).
    *   Tips for performance tuning (e.g., VAD integration, beam size, language detection).
    *   Troubleshooting common transcription issues.
7.  **Summarization Module (`docs/summarization_module.md`)**
    *   Interacting with OpenRouter.ai API.
    *   Prompt engineering guidelines (referencing `joules_v2_prompt_engineering_guidelines.md`).
    *   Alternative: Interacting with local LLMs (Ollama API, Python libraries).
    *   Handling long transcripts.
8.  **Tooling and Services (`docs/tooling_and_services.md`)**
    *   Full content from the previously generated `joules_v2_tooling_and_services.md`.
    *   This serves as a reference for all recommended free/OSS tools and services.
9.  **Performance, Privacy, and Fallbacks (`docs/performance_privacy_fallbacks.md`)**
    *   Full content from the previously generated `joules_v2_performance_privacy_fallbacks.md`.
    *   This section details how these critical aspects are handled in the project.
10. **Mobile App Extension Strategy (`docs/mobile_extension_strategy.md`)**
    *   Full content from the previously generated `joules_v2_mobile_extension_strategy.md`.
    *   Outlines plans and considerations for future mobile development.
11. **Testing Guide (`docs/testing.md`)**
    *   Strategy for unit tests (e.g., for utility functions, API handlers). Include examples if using a test runner like PyTest or Jest.
    *   Strategy for integration tests (e.g., testing frontend-backend communication, full processing pipeline with mock models).
    *   Manual testing checklist for core features and user flows.
    *   How to run tests and interpret results.
12. **Contribution Guidelines (`CONTRIBUTING.md`)**
    *   (Separate file, linked from README and docs)
    *   Detailed instructions on how to contribute (forking, branching strategy like Gitflow, code style guide, linter configurations).
    *   Process for submitting pull requests (PR template, review process).
    *   How to report bugs and suggest features (issue templates).
    *   Code of Conduct.
13. **Roadmap & Future Features (`docs/roadmap.md`)**
    *   Short-term and long-term goals for the project.
    *   Planned enhancements (e.g., PWA, Electron desktop application, advanced summarization techniques, multi-language support).
    *   **Advanced Mobile App:** Multi-user meeting support with link-based joining for guests.
    *   **Speaker Diarization:** Identifying 'who said what' in multi-participant meetings.
    *   **Web client for guests joining mobile-hosted meetings.**
    *   Calendar integration, real-time transcription.
    *   Community input mechanisms for roadmap suggestions.
14. **Troubleshooting Guide (`docs/troubleshooting.md`)**
    *   A curated list of common issues users or developers might encounter (e.g., installation problems, model errors, performance bottlenecks, browser compatibility).
    *   Step-by-step solutions and diagnostic tips for each issue.
15. **License Information (`LICENSE.md`)**
    *   (Separate file, linked from README)
    *   Full text of the chosen open-source license (e.g., MIT, Apache 2.0).

This comprehensive structure ensures that both users and developers have access to the information they need to use, understand, and contribute to Joules V2 (Free Edition).Okay, I will create the markdown document containing the README.md skeleton and a developer documentation outline for the Joules V2 (Free Edition) project.
