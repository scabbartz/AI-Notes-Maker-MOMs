'use strict';

// DOM Elements
const recordButton = document.getElementById('recordButton');
const stopButton = document.getElementById('stopButton');
// const downloadButton = document.getElementById('downloadButton'); // Optional, can be removed if not primary focus
const audioPlayback = document.getElementById('audioPlayback');
const audioFileInput = document.getElementById('audioFileInput');
const selectedFileName = document.getElementById('selectedFileName');
const uploadedAudioPlayback = document.getElementById('uploadedAudioPlayback');

const transcribeButton = document.getElementById('transcribeButton'); // Will now trigger both transcribe & summarize
const processingProgress = document.getElementById('processingProgress');
const progressMessage = document.getElementById('progressMessage');

const currentMeetingOutputSection = document.getElementById('currentMeetingOutputSection');
const transcriptOutput = document.getElementById('transcriptOutput');
const summaryOutput = document.getElementById('summaryOutput');
const saveMeetingButton = document.getElementById('saveMeetingButton');

const meetingList = document.getElementById('meetingList');
const clearHistoryButton = document.getElementById('clearHistoryButton');

// State Variables
let mediaRecorder;
let audioChunks = [];
let currentAudioBlob;
let stream;
let meetings = []; // Array to hold meeting objects {id, name, transcript, summary, timestamp}

const BACKEND_URL = 'http://localhost:5001';

// --- UI Update Functions ---
function showProcessingProgress(message) {
    progressMessage.textContent = message;
    processingProgress.style.display = 'block';
    transcribeButton.disabled = true;
}

function hideProcessingProgress() {
    processingProgress.style.display = 'none';
    enableTranscriptionButton(); // Re-evaluate if button should be enabled
}

function enableTranscriptionButton() {
    transcribeButton.disabled = !currentAudioBlob;
}

function displayCurrentMeetingOutput(transcript, summary) {
    transcriptOutput.value = transcript || "";
    summaryOutput.value = summary || "";
    currentMeetingOutputSection.style.display = 'block';
    saveMeetingButton.disabled = !(transcript && summary && !transcript.startsWith("Error:") && !summary.startsWith("Error:"));
}

function clearCurrentMeetingState() {
    currentAudioBlob = null;
    audioFileInput.value = null; // Reset file input
    selectedFileName.textContent = 'None';
    audioPlayback.src = '';
    audioPlayback.style.display = 'none';
    uploadedAudioPlayback.src = '';
    uploadedAudioPlayback.style.display = 'none';
    transcriptOutput.value = '';
    summaryOutput.value = '';
    currentMeetingOutputSection.style.display = 'none';
    saveMeetingButton.disabled = true;
    enableTranscriptionButton();
    recordButton.textContent = 'Record New Meeting'; // Reset record button text
    recordButton.disabled = false;
    stopButton.disabled = true;
}

// --- Recording & File Handling ---
recordButton.onclick = async () => {
    clearCurrentMeetingState(); // Clear previous state before new recording
    try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };
        mediaRecorder.onstop = () => {
            currentAudioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
            audioChunks = [];
            const audioUrl = URL.createObjectURL(currentAudioBlob);
            audioPlayback.src = audioUrl;
            audioPlayback.style.display = 'block';
            stopButton.disabled = true;
            recordButton.disabled = false;
            recordButton.textContent = 'Record New Meeting';
            selectedFileName.textContent = 'Using freshly recorded audio.';
            enableTranscriptionButton();
        };
        mediaRecorder.start();
        recordButton.disabled = true;
        stopButton.disabled = false;
        recordButton.textContent = 'Recording...';
    } catch (err) {
        console.error('Error starting recording:', err);
        alert('Could not start recording: ' + err.message);
        recordButton.disabled = false;
    }
};

stopButton.onclick = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        if (stream) stream.getTracks().forEach(track => track.stop());
    }
    recordButton.disabled = false;
    recordButton.textContent = 'Record New Meeting';
    stopButton.disabled = true;
};

audioFileInput.onchange = event => {
    clearCurrentMeetingState(); // Clear previous state
    const file = event.target.files[0];
    if (file) {
        currentAudioBlob = file;
        selectedFileName.textContent = file.name;
        const fileUrl = URL.createObjectURL(file);
        uploadedAudioPlayback.src = fileUrl;
        uploadedAudioPlayback.style.display = 'block';
        enableTranscriptionButton();
    } else {
        currentAudioBlob = null;
        selectedFileName.textContent = 'None';
        enableTranscriptionButton();
    }
};

// --- Transcription & Summarization (Combined) ---
transcribeButton.onclick = async () => {
    if (!currentAudioBlob) {
        alert('Please record or upload an audio file first.');
        return;
    }

    showProcessingProgress('Transcribing audio...');
    transcriptOutput.value = '';
    summaryOutput.value = '';
    currentMeetingOutputSection.style.display = 'none';

    const formData = new FormData();
    const fileName = currentAudioBlob.name || `recording.${currentAudioBlob.type.split('/')[1] || 'webm'}`;
    formData.append('audio_file', currentAudioBlob, fileName);

    let transcriptText = '';
    try {
        const transResponse = await fetch(`${BACKEND_URL}/transcribe`, {
            method: 'POST', body: formData,
        });
        if (transResponse.ok) {
            const result = await transResponse.json();
            transcriptText = result.transcript;
        } else {
            const errorResult = await transResponse.json();
            transcriptText = `Error transcribing: ${errorResult.error || transResponse.statusText}`;
            alert(`Transcription failed: ${errorResult.error || transResponse.statusText}`);
            hideProcessingProgress();
            displayCurrentMeetingOutput(transcriptText, '');
            return;
        }
    } catch (error) {
        console.error('Error during transcription request:', error);
        transcriptText = `Network error or server not responding during transcription: ${error.message}`;
        alert(`Could not connect to the transcription server: ${error.message}`);
        hideProcessingProgress();
        displayCurrentMeetingOutput(transcriptText, '');
        return;
    }

    // If transcription was successful, proceed to summarization
    if (transcriptText && !transcriptText.startsWith("Error:")) {
        showProcessingProgress('Summarizing transcript...');
        try {
            const sumResponse = await fetch(`${BACKEND_URL}/summarize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transcript: transcriptText }),
            });
            let summaryText = '';
            if (sumResponse.ok) {
                const result = await sumResponse.json();
                summaryText = result.summary;
            } else {
                const errorResult = await sumResponse.json();
                summaryText = `Error summarizing: ${errorResult.error || sumResponse.statusText}`;
                alert(`Summarization failed: ${errorResult.error || sumResponse.statusText}`);
            }
            displayCurrentMeetingOutput(transcriptText, summaryText);
        } catch (error) {
            console.error('Error during summarization request:', error);
            displayCurrentMeetingOutput(transcriptText, `Network error or server not responding during summarization: ${error.message}`);
            alert(`Could not connect to the summarization server: ${error.message}`);
        }
    } else {
        // Transcription failed, display transcript error, no summary
        displayCurrentMeetingOutput(transcriptText, '');
    }
    hideProcessingProgress();
};

// --- Meeting History / Dashboard Logic ---
function loadMeetings() {
    const storedMeetings = localStorage.getItem('joulesV2Meetings');
    if (storedMeetings) {
        meetings = JSON.parse(storedMeetings);
    }
    renderMeetingList();
}

function saveMeetings() {
    localStorage.setItem('joulesV2Meetings', JSON.stringify(meetings));
}

function renderMeetingList() {
    meetingList.innerHTML = ''; // Clear existing list
    if (meetings.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'No saved meetings yet.';
        li.className = 'empty-list-item';
        meetingList.appendChild(li);
        return;
    }
    meetings.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)); // Show newest first
    meetings.forEach(meeting => {
        const li = document.createElement('li');
        li.innerHTML = `
            <div class="meeting-info">
                <span class="meeting-name">${meeting.name}</span>
                <span class="meeting-timestamp">${new Date(meeting.timestamp).toLocaleString()}</span>
            </div>
            <div class="meeting-actions">
                <button class="view-btn" data-id="${meeting.id}">View</button>
                <button class="delete-btn" data-id="${meeting.id}">Delete</button>
            </div>
        `;
        meetingList.appendChild(li);
    });
}

saveMeetingButton.onclick = () => {
    const transcript = transcriptOutput.value;
    const summary = summaryOutput.value;
    if (!transcript || transcript.startsWith("Error:") || !summary || summary.startsWith("Error:")) {
        alert('Cannot save meeting with errors or empty fields.');
        return;
    }
    const defaultMeetingName = selectedFileName.textContent !== 'None' && selectedFileName.textContent !== 'Using freshly recorded audio.'
                               ? selectedFileName.textContent
                               : `Meeting ${new Date().toLocaleDateString()}`;
    const meetingName = prompt("Enter a name for this meeting:", defaultMeetingName);
    if (!meetingName) return; // User cancelled

    const newMeeting = {
        id: Date.now().toString(), // Simple unique ID
        name: meetingName,
        transcript: transcript,
        summary: summary,
        timestamp: new Date().toISOString()
    };
    meetings.unshift(newMeeting); // Add to the beginning of the list
    saveMeetings();
    renderMeetingList();
    alert('Meeting saved to dashboard!');
    // Optionally clear current meeting fields after saving
    // clearCurrentMeetingState();
};

meetingList.onclick = (event) => {
    const target = event.target;
    const meetingId = target.dataset.id;
    if (!meetingId) return;

    const meeting = meetings.find(m => m.id === meetingId);
    if (!meeting) return;

    if (target.classList.contains('view-btn')) {
        transcriptOutput.value = meeting.transcript;
        summaryOutput.value = meeting.summary;
        currentMeetingOutputSection.style.display = 'block';
        selectedFileName.textContent = meeting.name + " (from history)";
        // Disable processing buttons for viewed history items to avoid confusion
        transcribeButton.disabled = true;
        // saveMeetingButton.disabled = true; // Keep enabled if user wants to re-save with new name
    } else if (target.classList.contains('delete-btn')) {
        if (confirm(`Are you sure you want to delete meeting: "${meeting.name}"?`)) {
            meetings = meetings.filter(m => m.id !== meetingId);
            saveMeetings();
            renderMeetingList();
            // If the deleted meeting was being viewed, clear the view
            if (selectedFileName.textContent.startsWith(meeting.name)) { // Check if the currently viewed item is the one deleted
                 clearCurrentMeetingState();
            }
        }
    }
};

clearHistoryButton.onclick = () => {
    if (meetings.length === 0) {
        alert("Meeting history is already empty.");
        return;
    }
    if (confirm("Are you sure you want to delete ALL saved meetings? This cannot be undone.")) {
        meetings = [];
        saveMeetings();
        renderMeetingList();
        clearCurrentMeetingState();
        alert("All meeting history cleared.");
    }
};

// --- Initialization ---
function init() {
    clearCurrentMeetingState();
    loadMeetings();
}

init();
