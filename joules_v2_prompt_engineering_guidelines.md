# Joules V2 (Free Edition) - Prompt Engineering Guidelines for Meeting Summarization

This document provides guidelines and examples for crafting effective prompts to instruct Large Language Models (LLMs) for summarizing meeting transcripts within the Joules V2 application.

## 1. General Principles for Effective Prompts

*   **Be Specific and Clear:** The prompt should unambiguously state the desired task (e.g., "summarize," "extract action items," "generate Minutes of Meeting"). Avoid vague language.
*   **Provide Context:** Include relevant contextual information that can help the LLM understand the nature of the meeting. This might include:
    *   Meeting type (e.g., "team sync," "client onboarding," "project planning").
    *   Participants (if known, available, and appropriate considering privacy).
    *   Main topic or project being discussed.
*   **Define the Output Format:** Clearly specify the structure and format of the desired output. Use examples if necessary. Common formats include:
    *   Bulleted lists for key points or action items.
    *   Numbered lists for sequential information.
    *   Specific section headings (e.g., "Key Decisions," "Action Items," "Discussion Summary").
*   **Set the Tone and Style:** Indicate the desired tone (e.g., formal, informal) and style (e.g., concise, detailed, narrative) of the summary.
*   **Iterate and Refine:** Prompt engineering is an experimental process. Start with a foundational prompt and iteratively refine it based on the quality and accuracy of the LLM's output. Test with diverse transcripts.
*   **Use Role-Playing (System/User Messages):** For LLMs and APIs that support distinct system and user messages (e.g., OpenAI API, Anthropic Claude API, and some Ollama model interaction patterns), leverage this:
    *   **System Message:** Sets the overall persona, role, and high-level instructions for the AI assistant (e.g., "You are an expert meeting summarizer...").
    *   **User Message:** Contains the specific request for the current task, including the transcript and any immediate parameters.
*   **Instruction Placement:** For models/APIs without a dedicated system prompt, prepend instructions or role definitions at the beginning of the user prompt.

## 2. Example Prompts

Placeholders like `{transcript_text}`, `{meeting_topic}`, `{meeting_date}`, `{participant_names}` should be replaced by the application with actual data.

### A. Basic Concise Summary

*   **User Message:**
    ```
    Please provide a concise summary of the following meeting transcript. Focus on the main topics discussed and key outcomes.

    Transcript:
    """
    {transcript_text}
    """
    ```

### B. Detailed Summary with Key Points and Action Items

*   **System Message (Optional, but good practice for compatible APIs):**
    ```
    You are an AI assistant specializing in processing meeting transcripts. Your primary function is to produce clear, concise, and actionable meeting summaries. Ensure all action items are clearly identified with responsible parties if mentioned.
    ```
*   **User Message:**
    ```
    Meeting Transcript:
    """
    {transcript_text}
    """

    Based on the transcript provided above, please generate the following:
    1.  A brief overall summary of the meeting (approximately 2-3 sentences).
    2.  Key Discussion Points (as a bulleted list).
    3.  Action Items (as a bulleted list. For each item, clearly state the task, who is responsible if mentioned, and the deadline if specified. If no action items, state "No action items were identified.").
    ```

### C. Generating Minutes of Meeting (MOM)

*   **User Message:**
    ```
    Context:
    - Meeting Title/Topic: {meeting_topic} (e.g., "Weekly Project Sync - Alpha Feature Release")
    - Date: {meeting_date}
    - Participants (Optional, if available and privacy permits): {participant_names}

    Transcript:
    """
    {transcript_text}
    """

    Generate formal Minutes of Meeting (MOM) based on the provided context and transcript. The MOM should be structured as follows:

    ## Minutes of Meeting ##

    **Meeting Title:** {meeting_topic}
    **Date:** {meeting_date}
    **Attendees:** {participant_names_or_placeholder_if_none}

    **1. Agenda Items Discussed:**
    (Identify main agenda items or state "Agenda not explicitly stated, summary based on discussion flow.")

    **2. Key Decisions Made:**
    (List any explicit decisions reached during the meeting.)

    **3. Main Discussion Summary:**
    (Provide a neutral, factual summary of the core discussions.)

    **4. Action Items:**
    (List each action item clearly. Format: - [Task] - [Assigned to: Person/Team or 'Unassigned'] - [Due: Date or 'Not specified'])

    **5. Next Steps/Follow-up:**
    (Outline any agreed-upon next steps or follow-up meetings.)
    ```

### D. Extracting Only Action Items

*   **User Message:**
    ```
    Carefully review the following meeting transcript and extract all specific action items. For each action item, identify the task, the person or team responsible (if mentioned), and any stated deadline. If no action items are found, explicitly state "No action items identified."

    Transcript:
    """
    {transcript_text}
    """

    Please format the output as follows, with each action item on a new line:
    Action Item: [Description of the task] | Responsible: [Person/Team or "Not specified"] | Deadline: [Date or "Not specified"]
    ```

## 3. Handling Long Transcripts (Chunking and Aggregation)

LLMs have a finite context window (token limit). Transcripts longer than this limit need to be processed in chunks.

*   **Strategy 1: Simple Sequential Chunking & Summarization ("MapReduce" Style)**
    1.  **Split (Chunking):** Divide the long transcript into smaller, manageable chunks.
        *   *Size:* Each chunk should be well below the LLM's token limit (e.g., if the limit is 4096 tokens, aim for chunks of 1500-2500 tokens of text to leave room for prompt and response).
        *   *Overlap:* Use a small overlap between chunks (e.g., 100-200 words, or a few sentences) to help maintain context continuity across chunk boundaries.
        *   *Splitting Points:* If possible, try to split at natural breaks like speaker changes or paragraph ends, rather than mid-sentence.
    2.  **Summarize Each Chunk (Map Step):** Apply a specific summarization prompt to each chunk individually.
        *   *Prompt for individual chunk:*
            ```
            This is segment {chunk_number} of {total_chunks} from a longer meeting transcript. Please summarize the key discussion points, decisions, and any action items from ONLY this segment.

            Transcript Segment:
            """
            {chunk_text}
            """
            ```
    3.  **Aggregate Summaries (Reduce Step):** Combine the summaries generated from all individual chunks. Then, apply a final summarization prompt to this collection of chunk summaries to create a cohesive overall summary.
        *   *Prompt for final summary (after combining chunk summaries):*
            ```
            The following text consists of sequential summaries from different segments of a single, longer meeting. Please synthesize these partial summaries into a single, coherent, and comprehensive overall meeting summary. Identify overarching themes, key decisions made, and consolidate all action items mentioned across all segments. Avoid redundancy.

            Combined Partial Summaries:
            """
            {combined_chunk_summaries}
            """

            Final Comprehensive Summary:
            ```

*   **Strategy 2: Recursive Summarization**
    *   This is an extension of the above. If the combined chunk summaries are still too long, the aggregation step can be applied recursively: summarize groups of summaries until a final, manageable summary is achieved.

*   **Considerations for Chunking:**
    *   The ideal chunk size and overlap depend on the specific LLM and the nature of the content. Experimentation is key.
    *   Ensure the application logic correctly handles chunk numbering and the combination process.

## 4. System vs. User Messages (Adapting for Different APIs)

While APIs like OpenAI's Chat Completions have distinct `system`, `user`, and `assistant` roles, other APIs (like Ollama's `/api/generate` or some Hugging Face Inference API models) might expect a single `prompt` string.

*   **Example for Ollama (within the `prompt` field of the JSON payload):**
    The system-level instruction is prepended to the user's request within the main prompt.
    ```json
    {
      "model": "mistral", // Or any other model you're using with Ollama
      "prompt": "You are a highly skilled AI assistant whose expertise is to meticulously analyze meeting transcripts and generate concise, accurate summaries. Your summaries should highlight key discussion points, any decisions made, and all actionable items. Pay close attention to attributing action items if the information is available.\n\nNow, process the following meeting transcript:\n\n---\nTranscript Start\n---\n{transcript_text}\n---\nTranscript End\n---\n\nBased on this transcript, provide:\n1. A brief overall summary.\n2. Key Discussion Points (bulleted).\n3. Action Items (bulleted, with owner and deadline if specified).",
      "stream": false
    }
    ```

## 5. Iteration and Testing

*   **Model Variability:** The performance and nuances of LLMs vary significantly (e.g., GPT-3.5 vs. GPT-4, Mistral vs. LLaMA vs. Gemma). Test prompts across different models if you plan to support multiple.
*   **Diverse Data:** Test prompts with a wide range of transcript types:
    *   Short and long transcripts.
    *   Transcripts with clear speakers and those with interruptions or mumbled audio.
    *   Transcripts with many action items and those with none.
*   **Refine Based on Output:** Analyze the LLM's responses. If the output is not satisfactory, adjust the prompt:
    *   Be more or less prescriptive with formatting.
    *   Add or remove context.
    *   Rephrase instructions.
*   **Few-Shot Examples (Use Sparingly):** If an LLM consistently struggles with a specific format or task, you can include a few examples (input/output pairs) directly in the prompt. This is known as "few-shot prompting." However, this consumes valuable context window space.
    *   *Example (Few-shot for action item extraction within a larger prompt):*
        ```
        ...
        Extract action items. For example, if the transcript says "John will send the report by Friday", you should output: "Action: Send the report | Responsible: John | Deadline: Friday".
        If it says "We need to update the server", output: "Action: Update the server | Responsible: Not specified | Deadline: Not specified".

        Transcript:
        """
        {transcript_text}
        """
        ...
        ```

## 6. Placeholders in Prompts

*   Always use clear and consistent placeholders in your prompt templates (e.g., `{transcript_text}`, `{meeting_topic}`, `{meeting_date}`).
*   The application's backend logic is responsible for dynamically replacing these placeholders with the actual data before sending the request to the LLM. This ensures prompts are tailored to each specific meeting.

By following these guidelines, Joules V2 can more effectively leverage LLMs to provide valuable and accurate meeting summaries for its users.
