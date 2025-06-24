# Joules V2: Mobile App Extension Strategy for Multi-User Conversations

## Introduction and Overall Concept

This document outlines the strategy for extending Joules V2 to mobile platforms (iOS and Android), with a **new vision focused on facilitating multi-user conversations where each participant's audio is captured individually for enhanced speaker diarization and transcription accuracy.** This approach aims to move beyond individual recording to support collaborative meeting documentation.

The core ideas include:
*   **Mobile App as Host/Participant:** A native mobile app (iOS/Android) allows users to initiate or join meeting sessions.
*   **Individual Audio Streams:** Each participant (whether using the native app or a web client) records their audio on their own device. These individual streams are sent to a central backend.
*   **Speaker Diarization Focus:** The backend will process these streams to determine "who said what," which is crucial for accurate multi-speaker transcripts.
*   **Link-Based Joining:** Users without the native mobile app can join a session via a shareable web link, which opens a lightweight web client in their mobile (or desktop) browser for audio capture and participation.
*   **Privacy and FOSS Principles:** The strategy continues to emphasize user privacy and leverage free/open-source components where possible, though the multi-user aspect introduces new complexities in data handling and processing.

## 1. Choice of Mobile Development Framework

The choice of framework is crucial and depends on available expertise, desired performance, and development speed.

*   **React Native:**
    *   *Pros:*
        *   Utilizes JavaScript/React, potentially allowing for some code and logic reuse if the web frontend is React-based.
        *   Large and active community, extensive third-party libraries and tools.
        *   "Write once, run anywhere" (mostly) for iOS and Android.
        *   Hot reloading and fast refresh features speed up development.
        *   Can achieve near-native performance with careful optimization.
    *   *Cons:*
        *   Performance can degrade for very complex UIs or computationally intensive tasks if not well-optimized.
        *   The bridge communication between JavaScript and native modules can introduce overhead.
        *   Managing native dependencies and build issues can sometimes be complex.
    *   *Suitability:* A strong candidate if the development team (or individual) is already proficient in React. Good for applications with UIs that are not overly graphically intensive or require extreme performance for specific tasks better handled by native code.
    *   *Link:* [reactnative.dev](https://reactnative.dev/)

*   **Flutter:**
    *   *Pros:*
        *   Developed by Google, uses the Dart language.
        *   Known for excellent performance due to compilation to native ARM/x86 code.
        *   Expressive and flexible UI toolkit, allowing for custom designs and smooth animations.
        *   Fast development cycle with stateful hot reload.
        *   Growing community and a rich set of widgets.
        *   Single codebase for UI and business logic for both iOS and Android.
    *   *Cons:*
        *   Requires learning Dart and the Flutter widget framework.
        *   App size can sometimes be larger than truly native apps, though optimization is possible.
    *   *Suitability:* An excellent choice for applications demanding high performance and custom UIs. If starting a new mobile project or if the web frontend isn't React-based, Flutter presents a compelling option.
    *   *Link:* [flutter.dev](https://flutter.dev/)

*   **Native Development (Swift for iOS, Kotlin/Java for Android):**
    *   *Pros:*
        *   Best possible performance, direct access to all native device features and APIs.
        *   Optimal battery life and resource management.
    *   *Cons:*
        *   Requires separate codebases, development teams (or significantly more effort from one developer), and expertise for iOS and Android.
        *   Higher development costs and longer time-to-market.
    *   *Suitability:* Generally not recommended for this project given the "Free Edition" philosophy, limited resources, and the desire for rapid MVP development on mobile, unless a very specific native integration is paramount and unachievable via cross-platform tools.

*   **Progressive Web App (PWA):**
    *   *Pros:*
        *   Leverages the existing web application codebase.
        *   Installable to the user's home screen, providing an app-like experience.
        *   Can work offline to some extent using service workers.
        *   Access to some device features (e.g., camera, geolocation, limited background sync).
    *   *Cons:*
        *   Limited access to native device features compared to frameworks like React Native or Flutter (e.g., advanced background processing, full filesystem access, complex hardware interactions).
        *   Performance might not be as smooth as native or high-quality cross-platform apps, especially for intensive tasks.
        *   Audio recording capabilities, especially in the background or with screen off, can be heavily restricted by browser policies and OS limitations.
        *   Discoverability in app stores is not straightforward (though some stores are starting to list PWAs).
    *   *Suitability:* Could serve as a good initial step to make the web application more mobile-friendly and easily accessible from a home screen. It might be an interim solution or a complementary offering rather than a full replacement for a dedicated mobile app if advanced device features are needed.

**Framework Recommendation:**
For a new, dedicated mobile app, **Flutter** or **React Native** are the primary cross-platform choices.
*   If the web app is built with React and substantial logic can be reused, **React Native** might offer an advantage.
*   If aiming for high performance with a custom UI from a fresh start, or if React expertise isn't a driving factor, **Flutter** is often favored.

Given the project's open-source nature, the availability of free, high-quality plugins for audio recording, background processes, and communication (e.g., WebSockets, HTTP requests) within the chosen ecosystem will also be a key factor.

## 2. Core Functionality for Multi-User Mobile Experience

The mobile app and associated web client will need to support the following core functionalities for multi-user conversations:

*   **Meeting Session Initiation (App Users):**
    *   App users can create a new "meeting session."
    *   Upon creation, the backend generates a unique, shareable link for this session.
*   **Link-Based Joining & Web Client:**
    *   **Shareable Link:** The app user who initiated the meeting can share this link with other participants.
    *   **Web Client Access:** Participants clicking the link (on mobile or desktop) will open a lightweight web client in their browser.
    *   **Web Client Requirements:**
        *   **Audio Capture:** Utilize browser's `MediaRecorder` API (or similar WebRTC features) to capture audio from the participant's microphone.
        *   **Audio Transmission:** Ability to send captured audio chunks (e.g., via WebSockets or chunked HTTP POST requests) to the backend, associated with the correct meeting session ID.
        *   **Simple UI:** Minimal interface for users to input their name/designation and manage their recording status (mute/unmute, leave session).
*   **User Identification (Lightweight & Privacy-Focused):**
    *   **Prompt for Name:** The web client (and app for guest users if applicable) should prompt participants to enter a name or designation for the session.
    *   **Local Persistence (Web Client):** `localStorage` can be used on the web client to remember the user's entered name for that specific browser, making re-joining slightly easier for the same session link or future sessions from the same domain.
    *   **Session-Based Identity:** For the MVP, user identity is primarily session-based (i.e., the name they provide when joining). No central user accounts or persistent cross-session identity is planned to maintain simplicity and privacy.
    *   **Privacy Note:** Clearly communicate that names are used for speaker labeling in the current session and are not part of a persistent user profile.
*   **Individual Audio Capture and Transmission:**
    *   Each participant (whether using the native mobile app or the web client) records their audio on their own device.
    *   These individual audio streams (or chunks thereof) are sent to the backend, tagged with the meeting session ID and a unique participant identifier (which could be generated by the client or assigned by the backend upon joining).
*   **Native Mobile App UI:**
    *   Screens for initiating meetings, managing active sessions, viewing participants (by their chosen names), and accessing the final transcript/summary.
    *   Local recording controls and status indicators.

## 3. Transcription, Diarization, and Summarization Strategy

With multiple audio streams, the processing pipeline becomes more complex and heavily reliant on the backend.

*   **Backend API for Multi-User Sessions:** The backend (likely Python/Flask or FastAPI) will need to:
    *   Manage meeting sessions (creation, joining, ending).
    *   Handle uploads of multiple, potentially concurrent, audio streams per session.
    *   Orchestrate the diarization, transcription, and summarization processes.
    *   Serve the lightweight web client for link-based joiners.
*   **Speaker Diarization (Critical New Step):**
    *   **Goal:** To accurately identify "who said what" by processing the multiple individual audio streams received by the backend. This is essential for a coherent multi-speaker transcript.
    *   **Architectural Placement:** Diarization is a backend process that ideally occurs *before* final transcription or as an integral part of an advanced transcription workflow.
    *   **Approaches & Technologies:**
        *   **Backend Processing of Individual Streams:** The backend receives individual audio streams. It would then use a speaker diarization library (e.g., **`pyannote.audio`** as mentioned in `joules_v2_tooling_and_services.md`) to process these streams. This could involve analyzing each stream for voice activity and then comparing/clustering speaker characteristics across streams if they are not already uniquely identified by source.
        *   **Challenges:**
            *   **Accuracy:** High-quality diarization is notoriously difficult, especially with varying audio quality from different devices, background noise, cross-talk, and dynamic numbers of speakers.
            *   **Computational Cost:** Libraries like `pyannote.audio` can be resource-intensive (CPU/RAM, potentially GPU for faster processing), posing a challenge for a zero-cost, self-hosted backend unless the user has substantial hardware.
            *   **Synchronization:** Minor differences in recording start times or clock drift between clients could complicate segment alignment if not handled carefully. Sending audio in well-timestamped chunks can help.
        *   **Output:** The diarization process should aim to produce a temporal map of speaker segments (e.g., "Speaker A: 00:00:05-00:00:10", "Speaker B: 00:00:11-00:00:15"). This map is then used to attribute transcribed text.
    *   **Simplified MVP Approach for Diarization (Initial Fallback):**
        *   If full automated diarization is too complex or resource-intensive for an initial MVP, a simpler approach could be:
            *   Transcribe each user's stream separately.
            *   Label each transcript with the user's provided name (e.g., "Alice's Transcript:", "Bob's Transcript:").
            *   The final "merged" view might just be these separate, labeled transcripts presented sequentially or interleaved based on timestamps if available. The LLM summarizer would then be prompted to understand these are distinct speakers. This avoids the complexity of precise speech segment attribution but is less ideal than true diarization.
*   **Transcription:**
    *   Once diarization has produced speaker-segmented audio (or if using the simplified approach), the audio segments are transcribed using Whisper (via the backend, as per the existing architecture).
    *   If diarization provides speaker labels, the transcript should ideally incorporate these (e.g., "Alice: Hello everyone.", "Bob: Good to be here.").
*   **Summarization:**
    *   The final transcript (now ideally with speaker information from diarization) is sent by the backend to **OpenRouter.ai** for summarization, as per the updated primary strategy.
    *   The prompt sent to OpenRouter can be enhanced if reliable speaker information is available (e.g., "Summarize this meeting discussion. Pay attention to action items assigned to Alice, Bob, and Carol.").

*   **Option A: Reuse Existing Web Backend API (If a Backend is Developed)** - This section is now largely superseded by the multi-user backend requirements.
    *   *How it Works:* The mobile app records audio, then uploads the audio file to the same backend server (e.g., Python/Flask running on a user's PC or a cloud service) used by the web application. The backend performs transcription and summarization.
    *   *Pros:* (Original pros apply if this model is used for single-user recording by the app user, but less relevant for multi-user).
    *   *Cons:* (Original cons apply). For multi-user, the primary challenge is getting all streams to this backend and processing them.
    *   *Privacy:* For multi-user, all participant audio streams (from app and web clients) would be sent to this potentially user-hosted backend.

*   **On-Device Processing (Primarily for the App User's Own Audio - Limited Multi-User Scope):**
    *   *How it Works:* The native mobile app *could* still perform on-device transcription for the app user's *own* audio stream if desired for privacy/offline for that specific stream.
    *   **On-Device Transcription (`whisper.cpp`):** As originally described, this remains viable for the app user's local audio.
    *   **On-Device Summarization (LLMs via `llama.cpp` etc.):** Also viable for the app user's own data.
    *   *Limitations for Multi-User:* This on-device processing by the app user *does not directly solve the multi-user diarization problem*, as that requires access to all streams. It could, at best, provide a local transcript for the app user, which might then be sent as text to the backend to be combined with other (text or audio) inputs. This adds complexity.
    *   *Recommendation:* For the multi-user vision, backend-centric processing of all streams is likely more practical for achieving diarization. On-device processing could be a feature for "solo" recordings by the app user, separate from multi-user sessions.

*   **Hybrid Approach (Revised for Multi-User):**
    *   The "hybrid" nature now relates more to:
        *   Backend using FOSS for diarization/transcription vs. (hypothetical future) free-tier cloud services for these steps.
        *   Users choosing to have their summaries via OpenRouter vs. (if they set it up) a local LLM called by the backend.
    *   The core idea of processing all streams for diarization on a backend (user-hosted or otherwise) becomes central.

**Primary Strategy for Multi-User Mobile MVP:**
The backend (initially user-hosted as per Joules V2 philosophy) receives individual audio streams from all participants (app and web). This backend then orchestrates:
1.  **Speaker Diarization:** Using FOSS libraries (e.g., `pyannote.audio`). This is a key R&D area.
2.  **Transcription:** Using Whisper on the diarized audio segments.
3.  **Summarization:** Sending the final, speaker-attributed transcript to OpenRouter.ai.

## 4. Backend API Design for Multi-User Sessions (New Section)

The backend API needs to be designed to handle the multi-user workflow:

*   **Session Management Endpoints:**
    *   `POST /api/sessions/create`: Initiates a new meeting session, returns a unique session ID and shareable link.
    *   `GET /api/sessions/{session_id}/join_info`: (Optional) Provides info needed for a client to join.
    *   `POST /api/sessions/{session_id}/end`: (Host only) Ends the session.
*   **Audio Handling Endpoints:**
    *   `POST /api/sessions/{session_id}/upload_audio_chunk`: Endpoint for clients (app or web) to upload audio chunks. This should handle multiple simultaneous uploads from different participants. WebSockets (e.g., using `Flask-SocketIO` or `FastAPI WebSockets`) might be more suitable than HTTP for streaming audio chunks to minimize latency and manage client connections.
    *   Each chunk should be tagged with a persistent participant identifier for that session.
*   **Web Client Serving:**
    *   `GET /join/{session_id}`: Serves the lightweight web client page for users joining via a link.
*   **Results Endpoints:**
    *   `GET /api/sessions/{session_id}/transcript`: Retrieves the processed transcript (with speaker attribution).
    *   `GET /api/sessions/{session_id}/summary`: Retrieves the summary.
    *   (Consider WebSockets for pushing updates to clients when processing is complete).

## 5. Storage on Mobile (and Backend Implications)

*   **Local Device Storage:**
    *   Primary storage for audio recordings, generated transcripts, and summaries.
    *   Utilize standard file system access provided by the chosen framework:
        *   Flutter: `path_provider` package to get appropriate directory paths.
        *   React Native: `react-native-fs` library or similar.
*   **Local Database (Optional, for Metadata):**
    *   To manage metadata associated with recordings (e.g., title, date, duration, processing status, tags).
    *   `sqflite` (Flutter) or `SQLite` (React Native via a community library) for a local relational database.
    *   Lightweight key-value stores like Hive (Flutter) or AsyncStorage (React Native, for very simple data) could also be considered for settings or basic metadata.
*   **Cloud Sync (Future, User-Controlled, Optional):**
    *   Allow users to *optionally* connect to their *own* cloud storage services (e.g., Google Drive, Dropbox, Nextcloud) for backup or synchronization across their devices.
    *   This would require using the respective cloud provider's mobile SDKs/APIs and handling OAuth authentication.
    *   This feature must be strictly opt-in and prioritize user privacy and control over their data.
*   **Backend Storage:** The backend will need to temporarily store incoming audio streams/chunks from all participants for a given session until they are processed. Policies for data retention (e.g., delete audio after successful transcription and summarization, or after a short configurable period like 24 hours) must be clearly defined and communicated. Transcripts and summaries might be stored longer if the backend also serves as the retrieval point for users, again with clear policies.

## 6. Security and Privacy for Multi-User Scenarios (Expanded Section)

The multi-user dimension introduces new security and privacy aspects:

*   **Link Sharing and Session Access:**
    *   *Risk:* Unique meeting links, if shared indiscriminately, could lead to unintended participants joining a session.
    *   *Mitigation (MVP):* For MVP, the primary protection is the obscurity of the generated link. Clear warnings to the host about responsible link sharing are needed.
    *   *Mitigation (Future):* Implementations like a "waiting room" where the host (app user who created the session) approves participants, or password-protected sessions, could be considered but add significant complexity.
*   **Data Handling by Backend:**
    *   The backend (even if user-hosted) will temporarily handle audio data from all participants.
    *   **Transparency:** All participants (app and web client users) must be clearly informed that their audio is being recorded, sent to a backend for processing (transcription, diarization), and that the transcript will be used for summarization (potentially via a third-party like OpenRouter).
    *   **Data Retention:** The backend's data retention policy for session audio, transcripts, and summaries needs to be clear. For a privacy-focused, user-hosted backend, the default should be to minimize retention, perhaps deleting audio immediately after processing and transcripts/summaries after a short, configurable period or when the host explicitly deletes them.
*   **Encryption:**
    *   **In Transit:** Standard HTTPS for web client communication and app-to-backend communication will protect data in transit to the backend. Audio chunks sent via WebSockets should use WSS (secure WebSockets).
    *   **End-to-End Encryption (E2EE):** True E2EE for multi-party audio where the server cannot access raw audio is very complex to achieve if the server needs to perform diarization and transcription. The current model (streams to backend for processing) does not assume E2EE of content from the server.
*   **Consent:**
    *   **Web Client Joiners:** Must be presented with a clear notice about audio recording, processing, and data handling *before* they activate their microphone and join the session. A simple "Accept to Join" after displaying this information is crucial.
    *   **App Users:** The app's privacy policy should cover multi-user session data handling.

## 7. Development Plan & Milestones for Mobile App (Revised for Multi-User)

1.  **Framework Selection & Basic App Shell:** (As before) Choose React Native or Flutter, set up project, basic navigation.
2.  **Individual Audio Recording (App):** Implement robust audio recording and local saving for the app user (for potential solo use or as a participant).
3.  **Backend - Initial Session Management:**
    *   Develop API endpoints for creating a session and generating a unique shareable link.
    *   Basic mechanism to associate incoming data with a session ID.
4.  **Web Client for Link Joiners (MVP v1):**
    *   Develop the lightweight web client.
    *   Implement audio capture (MediaRecorder).
    *   Implement user name input.
    *   Ability to send audio chunks and participant name to the backend, associated with the session ID.
    *   Clear consent mechanism.
5.  **Backend - Receiving Multiple Streams:**
    *   Develop backend logic to receive and temporarily store audio chunks from multiple participants (app and web clients) for a given session.
6.  **Simplified Diarization & Transcription (MVP v1.5):**
    *   Initially, transcribe each stream separately.
    *   Label transcripts with participant names.
    *   Send these labeled (but not fully interleaved/diarized) transcripts to OpenRouter for an initial attempt at summarization.
7.  **Backend - Automated Speaker Diarization R&D (MVP v2 / Post-MVP):**
    *   Integrate and test a FOSS diarization library (e.g., `pyannote.audio`) with the multiple audio streams.
    *   Refine the process to generate a speaker-attributed transcript.
    *   Update summarization prompts to leverage speaker information.
8.  **Full Integration & UI/UX:** Display diarized transcripts and summaries in the app and potentially a view for web clients. Refine UI/UX for managing multi-user sessions.
9.  **(Later) On-Device Processing for App User (Solo Mode):** If desired, implement on-device transcription/summarization for the app user when not in a multi-user session.

## 8. Key Trade-offs and Considerations (Revised for Multi-User)

*   **Increased Complexity:** The multi-user, diarized approach is significantly more complex than the original individual recording mobile strategy, especially concerning backend logic, audio stream management, and diarization.
*   **Accuracy of Speaker Diarization:** This is a major technical hurdle. Achieving high accuracy with FOSS tools under zero-cost infrastructure constraints (i.e., user-hosted server that might not be powerful) will be challenging. Results will vary based on audio quality, number of speakers, and overlap.
*   **User Experience (UX):** Managing multiple audio sources, ensuring reasonable synchronization, handling users joining/leaving sessions, and presenting multi-speaker transcripts effectively requires careful UX design.
*   **Backend Resource Demands:** Processing multiple audio streams and running diarization algorithms will be demanding on the backend server's CPU and RAM. This is a key consideration if users are self-hosting the backend on typical consumer hardware.
*   **Network Dependency:** Unlike a fully on-device solo app, this model inherently relies on network connectivity for all participants to communicate with the backend.
*   **Scalability of User-Hosted Backend:** A user-hosted backend might struggle if many participants join a session simultaneously, overwhelming its capacity.

## Conclusion (Revised)

Extending Joules V2 to mobile with a multi-user conversation focus, including link-based joining and speaker diarization, represents a significant evolution of the project's vision. This approach enhances its collaborative potential but also introduces substantial technical complexities, particularly around backend development, audio processing, and achieving accurate speaker diarization under the project's FOSS and free-tier principles.

The recommended strategy involves prioritizing backend capabilities for session management and multi-stream audio handling, developing a lightweight web client for broad accessibility, and tackling speaker diarization iteratively, potentially starting with simpler approaches. While on-device processing for the app user's solo recordings remains a valuable option for privacy, the multi-user scenario will primarily rely on a robust (initially user-hosted) backend. Clear communication about privacy, data handling, and the experimental nature of advanced features like diarization will be essential.
