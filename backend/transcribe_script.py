# backend/transcribe_script.py
import whisper
import sys
import os
import time

# Recommended model sizes for general use on CPU: "tiny", "base", "small"
# "medium" and "large" are more accurate but much slower on CPU and require more RAM.
DEFAULT_MODEL_SIZE = "base"

def transcribe_audio(audio_file_path, model_size=DEFAULT_MODEL_SIZE):
    """Transcribes an audio file using OpenAI Whisper.

    Args:
        audio_file_path (str): The path to the audio file.
        model_size (str): The Whisper model size to use (e.g., "tiny", "base", "small").

    Returns:
        str: The transcript text, or an error message if transcription fails.
    """
    if not os.path.exists(audio_file_path):
        return f"Error: Audio file not found at {audio_file_path}"

    print(f"Loading Whisper model '{model_size}'...")
    try:
        # Model loading can be time-consuming, especially the first time
        # or for larger models.
        model = whisper.load_model(model_size)
        print(f"Whisper model '{model_size}' loaded successfully.")
    except Exception as e:
        return f"Error loading Whisper model '{model_size}': {e}\nEnsure you have the model files downloaded or sufficient internet access for automatic download. You might also need ffmpeg installed."

    print(f"Starting transcription for {audio_file_path}...")
    start_time = time.time()
    try:
        # For CPU, fp16=False is important. fp16 is for NVIDIA GPUs.
        # For potentially long audio, consider parameters like `temperature` or using VAD (Voice Activity Detection)
        # if Whisper version supports it directly or via an external library for pre-processing.
        # The `language` parameter can be specified if known, e.g., language='en'
        result = model.transcribe(audio_file_path, fp16=False)
        transcript = result["text"]
        end_time = time.time()
        print(f"Transcription completed in {end_time - start_time:.2f} seconds.")
        return transcript
    except Exception as e:
        return f"Error during transcription: {e}"

if __name__ == "__main__":
    # Check if an audio file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python transcribe_script.py <path_to_audio_file> [model_size]")
        print(f"Example: python transcribe_script.py meeting_audio.wav {DEFAULT_MODEL_SIZE}")
        print(f"Available model sizes (generally, smaller is faster but less accurate): tiny, base, small, medium, large")
        sys.exit(1) # Exit with an error code

    audio_path_arg = sys.argv[1]

    # Optional model_size argument
    model_size_arg = DEFAULT_MODEL_SIZE
    if len(sys.argv) > 2:
        model_size_arg = sys.argv[2]
        if model_size_arg not in ['tiny', 'base', 'small', 'medium', 'large']:
            print(f"Warning: Model size '{model_size_arg}' not recognized. Using default '{DEFAULT_MODEL_SIZE}'.")
            model_size_arg = DEFAULT_MODEL_SIZE

    print(f"Processing audio file: {audio_path_arg}")
    print(f"Using Whisper model size: {model_size_arg}")

    transcript_output = transcribe_audio(audio_path_arg, model_size_arg)

    # Print the transcript or error message
    # A more structured output (e.g., JSON) might be better if this script were
    # to be called by other programs frequently, but for now, plain text is fine.
    print("\n--- Transcript ---")
    print(transcript_output)
    print("--- End of Transcript ---")

# To run this script (assuming it's in a 'backend' directory):
# cd backend
# python transcribe_script.py ../frontend/meeting_audio.wav base
# (This assumes you've previously recorded and downloaded an audio file to frontend/meeting_audio.wav)

# Dependencies for this script (to be included in backend/requirements.txt later):
# openai-whisper
# (Whisper also depends on numpy and torch; these will be installed as dependencies of openai-whisper)
# (User also needs ffmpeg installed on their system and available in PATH for Whisper to process various audio formats)
