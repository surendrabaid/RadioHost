# Technical Design Document: The Synthetic Radio Host

## 1. Project Overview
**Track:** AI-Powered Content Creation (Wikipedia to Audio Pipeline)

The **The Synthetic Radio Host** is an automated pipeline that transforms Wikipedia articles into engaging, natural-sounding, two-person Hinglish (Hindi + English) podcasts. It bridges the gap between static information and dynamic, conversational audio content, optimized for the young Indian demographic.

## 2. System Architecture

### 2.1 Flow Diagram
The system follows a linear, robust pipeline with built-in fallbacks:

```text
[Topic Input] 
      │
      ▼
┌──────────────┐      ┌───────────────────────────┐
│  Wikipedia   │─────▶│ Raw Requests (Verify=Off) │ (Fallback)
│  API Fetch   │      └───────────────────────────┘
└──────────────┘                    │
      │                             ▼
      ▼                       ┌───────────┐
┌──────────────┐              │  Dummy    │ (Last Resort)
│   Context    │◀─────────────│  Content  │
│   Refining   │              └───────────┘
└──────────────┘
      │
      ▼
┌──────────────┐      ┌───────────────────────────┐
│ GPT-5 Mini   │─────▶│ Hinglish Script (JSON)    │
│ Script Gen   │      │ (8-10 Dialogue Turns)     │
└──────────────┘      └───────────────────────────┘
      │
      ▼
┌──────────────┐      ┌───────────────────────────┐
│ GPT-4o Audio │─────▶│ Multimodal Audio Buffer   │
│ (Steerable)  │      │ (Base64 Decoding)         │
└──────────────┘      └───────────────────────────┘
      │
      ▼
┌──────────────┐
│  MP3 Output  │
│ (< 2 Mins)   │
└──────────────┘
```

### 2.2 Key Components
1.  **Data Ingestion Layer**: Fetches data from Wikipedia. Includes an SSL-patching layer using `certifi` and a raw `requests` fallback to handle restrictive network environments (like macOS/Anaconda).
2.  **Linguistic Processing Layer (GPT-5 Mini)**: Uses a specialized system prompt to convert dry facts into Hinglish dialogue. It enforces conversational markers (`[laughs]`, `umm...`) and strictly limits turns to ensure the audio duration stays under 2 minutes.
3.  **Acoustic Generation Layer (GPT-4o Audio)**: Unlike standard TTS, this layer uses speech-to-speech logic. It provides specific instructions to the model to apply an Indian accent and perform emotional prosody (real laughter/breathing).

---

## 3. Setup and Deployment

### 3.1 Prerequisites
- Python 3.10+
- OpenAI API Key (with GPT-5 and GPT-4o access)

### 3.2 Installation
1.  **Clone the project** to your local directory.
2.  **Install dependencies**:
    ```bash
    pip install openai wikipedia-api python-dotenv requests certifi
    ```
3.  **SSL Configuration (Critical for Mac)**:
    If running on macOS, ensure your certificates are updated:
    ```bash
    /Applications/Python\ 3.x/Install\ Certificates.command
    ```

### 3.3 Deployment
1.  **Environment Variables**: Create a `.env` file or export the key:
    ```bash
    export OPENAI_API_KEY="your-key-here"
    ```
2.  **Execution**:
    ```bash
    python podcast_generator.py
    ```

---

## 4. Code Explanations & Assumptions

### 4.1 Detailed Code Logic Explanations

#### **A. The SSL & Environment Patch (L11-L22)**
*   **Problem**: macOS users (especially those using Anaconda) frequently encounter `CERTIFICATE_VERIFY_FAILED` errors because the environment lacks a modern CA bundle.
*   **Solution**: The code imports `certifi` and monkeypatches the global SSL context during initialization. By force-pointing `ssl._create_default_https_context` to the Certifi bundle, we ensure that the Wikipedia API and OpenAI client can establish secure connections without manual system-wide certificate installation.

#### **B. Double-Layer Robust Data Ingestion (L37-L83)**
*   **Standard Path**: Uses the `wikipedia-api` Python wrapper for structural data.
*   **Insecure Fallback**: If the wrapper fails (due to strict server-side blocking or local SSL issues), the code switches to a raw `requests` call using the MediaWiki JSON API. 
*   **Manual User-Agent**: Wikipedia blocks "anonymous" scripts. We explicitly set a unique `USER_AGENT` header to comply with the Wikimedia Robot Policy while providing a high-availability data source.

#### **C. Linguistic Turn-Limiting for Duration (L119-L141)**
*   **Logic**: Word counts are notoriously unreliable in LLM prompting. Instead, the generator uses **Dialogue Turn Constraints** (8–10 turns).
*   **Acoustic Math**: At an average conversational rate of 140 words per minute, 180 words (the result of ~10 turns) provides approximately 80–90 seconds of audio. This 30-second "buffer" allows for natural breathing, laughter pauses, and intros, ensuring the output never exceeds the 120-second (2-minute) limit.

#### **D. Multimodal Audio Steerability (L175-L193)**
*   **Innovation**: We avoid standard 1-way TTS (`tts-1`) in favor of GPT-4o's **audio modalities**.
*   **Prosodic Control**: By providing the instruction *"Use a natural, expressive Indian accent"* in the system role, the model performs a native-sounding accent instead of a neutral American one.
*   **Performance vs Reading**: The model "performs" markers like `[laughs]` or `[sighs]` as actual sounds, creating a high-fidelity "conversational" feel.

### 4.2 Core Project Assumptions

1.  **Archetype-Driven Hinglish**: We assume that Hinglish is most authentic when the AI "acts" (Persona-based) rather than "translates." Defining Kabir and Ananya as specific archetypes ensures natural code-switching.
2.  **Constant Word-to-Time Ratio**: We assume a predictable speaking pace (approx 2.5 words per second). This allows us to calculate duration based on dialogue turn complexity.
3.  **Network Resilience over Security**: In the Wikipedia fallback path, we assume that "Availability is King." Thus, `verify=False` is used to ensure the content is fetched even in highly restrictive network environments.
4.  **Hardware Independence**: The script assumes no local GPU or specialized audio libraries (like `ffmpeg`) are available. Therefore, we use OpenAI's cloud-based audio processing and simple byte-level file concatenation to produce the MP3.
