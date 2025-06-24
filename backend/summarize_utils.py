# backend/summarize_utils.py
import os
import requests
import json
import logging
import sys # Added for sys.exit in main block

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Refer to OpenRouter documentation for currently available free models.
# Some good candidates often found on free tiers:
# - "mistralai/mistral-7b-instruct:free"
# - "nousresearch/nous-hermes-2-mixtral-8x7b-dpo:free"
# - "gryphe/mythomist-7b:free"
# Using a placeholder, user should verify and pick one.
DEFAULT_SUMMARIZATION_MODEL = "mistralai/mistral-7b-instruct:free"
# Or: "nousresearch/nous-hermes-2-mixtral-8x7b-dpo:free" - tends to be good for instruction following

# Configure basic logging for this module
logger = logging.getLogger(__name__)
if not logger.handlers: # Avoid adding multiple handlers if script is reloaded or imported multiple times
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO) # Set default logging level for the module

def get_default_summary_prompt(transcript):
    """Returns a default prompt for summarization."""
    return f"""Please provide a concise summary of the following meeting transcript.
Focus on the main topics discussed, key decisions made, and any explicitly stated action items.
Structure the output clearly.

Transcript:
"""
{transcript}
"""

Summary:"""

def summarize_transcript_with_openrouter(transcript, model_name=DEFAULT_SUMMARIZATION_MODEL, prompt_template_func=get_default_summary_prompt):
    """Sends a transcript to OpenRouter.ai for summarization.

    Args:
        transcript (str): The transcript text to summarize.
        model_name (str): The OpenRouter model to use (e.g., "mistralai/mistral-7b-instruct:free").
        prompt_template_func (function): A function that takes the transcript and returns the full prompt string.

    Returns:
        str: The summary text, or an error message if summarization fails.
    """
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY environment variable not set.")
        return "Error: OpenRouter API key not configured on the server."

    if not transcript or not transcript.strip():
        logger.warning("Empty transcript provided for summarization.")
        return "Error: Cannot summarize an empty transcript."

    full_prompt = prompt_template_func(transcript)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Recommended by OpenRouter:
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000"), # Your app's site URL
        "X-Title": os.getenv("OPENROUTER_APP_TITLE", "Joules V2 Free Edition") # Your app's name
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": full_prompt}
        ],
        # "max_tokens": 500, # Optional: Adjust based on expected summary length and model limits
        # "temperature": 0.7, # Optional: Adjust for creativity vs. determinism
    }

    logger.info(f"Sending request to OpenRouter with model: {model_name}")
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=120) # 120 seconds timeout
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        response_data = response.json()

        if response_data.get("choices") and len(response_data["choices"]) > 0:
            message_content = response_data["choices"][0].get("message", {}).get("content")
            if message_content:
                summary = message_content
                logger.info("Summary received successfully from OpenRouter.")
                return summary.strip()
            else:
                logger.error(f"Empty message content in OpenRouter response: {response_data}")
                return f"Error: Empty summary content in OpenRouter response. Details: {response_data.get('error', {}).get('message', str(response_data))}"

        else:
            logger.error(f"Unexpected response structure from OpenRouter (no choices or empty choices): {response_data}")
            return f"Error: Could not extract summary from OpenRouter response. Details: {response_data.get('error', {}).get('message', str(response_data))}"

    except requests.exceptions.Timeout:
        logger.error(f"Request to OpenRouter timed out after 120 seconds.")
        return "Error: The summarization request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        error_text = "No response"
        if e.response is not None:
            error_text = e.response.text
            try: # Try to parse JSON error from OpenRouter
                json_error = e.response.json()
                if isinstance(json_error, dict) and json_error.get("error"):
                    error_text = json_error["error"].get("message", str(json_error["error"]))
            except json.JSONDecodeError:
                pass # Use raw text if not JSON
        logger.error(f"Error calling OpenRouter API: {e}. Response: {error_text}")
        return f"Error communicating with OpenRouter: {error_text}"
    except Exception as e:
        logger.error(f"An unexpected error occurred during summarization: {e}", exc_info=True)
        return f"An unexpected error occurred: {str(e)}"

if __name__ == '__main__':
    # This block is for testing the function directly.
    # Ensure OPENROUTER_API_KEY is set as an environment variable before running.
    print("Testing summarization function...")
    if not OPENROUTER_API_KEY:
        print("CRITICAL ERROR: OPENROUTER_API_KEY environment variable is not set. Please set it to test.")
        print("Example: export OPENROUTER_API_KEY='your_api_key_here'")
        sys.exit(1)

    sample_transcript = ("Alice: Good morning everyone. Today we're discussing the Q3 project status. Bob, can you start with the engineering update? "
                       "Bob: Sure, Alice. We've completed modules A and B. Module C is 70% done, expecting full completion by next Friday. We hit a small snag with the database integration but it's resolved now. "
                       "Alice: Great progress, Bob. Carol, any updates from marketing? "
                       "Carol: Yes, the initial campaign drafts are ready and we've identified key influencers. We're on track for the launch if engineering delivers module C on time. "
                       "Alice: Excellent. So, key action items are: Bob to ensure Module C is completed by next Friday. Carol to finalize campaign materials post Module C completion. Any questions? No? Okay, meeting adjourned.")

    print(f"\nUsing model: {DEFAULT_SUMMARIZATION_MODEL}")
    summary_result = summarize_transcript_with_openrouter(sample_transcript)
    print("\n--- Summary ---")
    print(summary_result)
    print("--- End of Summary ---")

    # Test with an empty transcript
    print("\nTesting with empty transcript...")
    empty_summary = summarize_transcript_with_openrouter("")
    print(f"Empty transcript summary attempt: {empty_summary}")

    # Test with a different model (example, user should ensure this model is free/available on OpenRouter)
    # Note: Using a potentially non-free or different model for testing might incur costs or fail if not available.
    # TEST_MODEL_ALT = "anthropic/claude-3-haiku-20240307"
    # print(f"\nAttempting to use alternative model: {TEST_MODEL_ALT} (ensure it's available on your OpenRouter plan)")
    # summary_result_alt = summarize_transcript_with_openrouter(sample_transcript, model_name=TEST_MODEL_ALT)
    # print("\n--- Summary (Alt Model) ---")
    # print(summary_result_alt)
    # print("--- End of Summary (Alt Model) ---")

    # Test API key error (by temporarily unsetting, not feasible in this script execution)
    # print("\nTesting with invalid API key (simulated - this test won't actually unset the key)...")
    # temp_key = OPENROUTER_API_KEY
    # OPENROUTER_API_KEY = "invalid_key_for_testing"
    # error_summary = summarize_transcript_with_openrouter(sample_transcript)
    # print(f"Invalid API key summary attempt: {error_summary}")
    # OPENROUTER_API_KEY = temp_key # Reset key
    # print("Note: True API key error testing requires running with an actual invalid key set in environment.")
