A Python pipeline that takes a Wikipedia article (e.g., about "Mumbai Indians"), generates a natural-sounding 2-minute conversation script between two people in Hinglish (using an LLM), and then converts it into audio using a TTS API
# Hinglish Podcast Generator

This project generates a conversational Hinglish podcast between two AI hosts about any topic found on Wikipedia.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **API Key:**
    You need an OpenAI API key (for GPT-4 and TTS-1).
    Create a `.env` file in this directory:
    ```
    OPENAI_API_KEY=sk-your-key-here
    ```
    Or set it in your environment.

## Usage

Run the script:
```bash
python podcast_generator.py
```
Enter a topic when prompted (e.g., "Mumbai Indians" or "Virat Kohli").

## Output

-   `script.json`: The generated conversation script.
-   `hinglish_podcast.mp3`: The final audio file.

## Design Decisions & Constraints

-   **Conversational Logic**: The script uses a highly specific system prompt to enforce "Hinglish", natural interruptions, and filler words.
-   **Audio**: Uses OpenAI's `tts-1` model with `onyx` (Kabir) and `nova` (Ananya) voices for dynamic contrast. The script combines their lines into a single audio file.
-   See `EXPLANATION.md` for details on the prompting strategy.

**Note:** If you encounter SSL errors on Mac, ensure your Python installation has valid certificates (run `Install Certificates.command` in your Python folder) or use the fallback logic included in the script.
