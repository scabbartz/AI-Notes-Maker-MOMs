# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import logging

from transcribe_script import transcribe_audio, DEFAULT_MODEL_SIZE
from summarize_utils import summarize_transcript_with_openrouter # Import the new function

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# ... (transcribe_endpoint and other existing code from app.py) ...
# (Keep the existing /transcribe endpoint as is)

@app.route('/transcribe', methods=['POST'])
def transcribe_endpoint():
    logging.info("'/transcribe' endpoint hit")
    if 'audio_file' not in request.files:
        logging.warning("No audio file part in request")
        return jsonify({"error": "No audio file part"}), 400

    file = request.files['audio_file']
    if file.filename == '':
        logging.warning("No selected file in request")
        return jsonify({"error": "No selected file"}), 400

    if file:
        temp_dir = tempfile.mkdtemp()
        # Ensure the filename from the upload is safe to use for path construction
        filename = os.path.basename(file.filename) if file.filename else "uploaded_audio"
        # Basic sanitization - replace potentially problematic characters
        safe_filename = "".join(c if c.isalnum() or c in ('.', '_', '-') else '_' for c in filename)
        if not safe_filename: # Handle cases where filename becomes empty after sanitization
            safe_filename = "uploaded_audio_fallback"

        temp_audio_path = os.path.join(temp_dir, safe_filename)

        try:
            file.save(temp_audio_path)
            logging.info(f"Audio file saved temporarily to {temp_audio_path}")
            transcript_text = transcribe_audio(temp_audio_path, model_size=DEFAULT_MODEL_SIZE)
            if transcript_text.startswith("Error:"):
                logging.error(f"Transcription failed: {transcript_text}")
                return jsonify({"error": transcript_text}), 500
            logging.info(f"Transcription successful for {safe_filename}")
            return jsonify({"transcript": transcript_text})
        except Exception as e:
            logging.error(f"An error occurred during transcription processing: {e}", exc_info=True)
            return jsonify({"error": f"An internal server error occurred during transcription: {str(e)}"}), 500
        finally:
            try:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                # Only remove dir if it's empty and it's the one we created
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
                logging.info(f"Temporary file {temp_audio_path} and directory {temp_dir} (if empty) cleaned up.")
            except Exception as e:
                logging.error(f"Error during cleanup: {e}", exc_info=True)
    else:
        logging.error("File object somehow became invalid after initial checks.")
        return jsonify({"error": "File processing error after initial checks"}), 500

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    logging.info("'/summarize' endpoint hit")
    data = request.get_json()

    if not data or 'transcript' not in data:
        logging.warning("No transcript provided in summarize request")
        return jsonify({"error": "Missing transcript in request body"}), 400

    transcript = data['transcript']
    if not transcript.strip():
        logging.warning("Empty transcript provided for summarization")
        return jsonify({"error": "Cannot summarize an empty transcript"}), 400

    logging.info(f"Received transcript for summarization (first 100 chars): {transcript[:100]}...")

    # Call the summarization function from summarize_utils
    # Model selection can be added as a parameter here if needed later
    summary_text = summarize_transcript_with_openrouter(transcript)

    if summary_text.startswith("Error:"):
        logging.error(f"Summarization failed: {summary_text}")
        return jsonify({"error": summary_text}), 500

    logging.info("Summarization successful.")
    return jsonify({"summary": summary_text})

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
