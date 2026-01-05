# If running in Colab, uncomment the next line:
# !pip install openai wikipedia-api python-dotenv

import os
import json
import wikipediaapi
from openai import OpenAI
from dotenv import load_dotenv
import certifi

# Fix SSL certificate issues (especially on macOS)
try:
    import ssl
    import certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl._create_default_https_context = lambda: ssl_context
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    os.environ['SSL_CERT_FILE'] = certifi.where()
except Exception as e:
    print(f"Warning: Could not patch SSL context: {e}")

USER_AGENT = 'HinglishPodcastBot/1.0 (contact@example.com)'

# Load environment variables
load_dotenv()

# Configuration
# Users verify their OpenAI key is in .env or environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not found. Using dummy key for initialization.")
    print("The script will fetch Wikipedia data but fail at LLM generation.")
    api_key = "sk-dummy-key-for-initialization"

client = OpenAI(api_key=api_key)

def get_wikipedia_content(topic, lang='en'):
    """Fetches the summary and first section of a Wikipedia article."""
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
            user_agent=USER_AGENT,
            language=lang
        )
        page = wiki_wiki.page(topic)
        if not page.exists():
            return None
        return page.summary[:4000]
    except Exception as e:
        print(f"Error fetching Wikipedia data: {e}")
        print("Attempting fallback with raw requests...")
        import requests
        
        try:
            # Fallback to direct API call
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": topic,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
            }
            # Include User-Agent in headers
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(url, params=params, headers=headers, verify=False)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1":
                    content = page_data.get("extract", "")[:4000]
                    if content:
                        print("Wikipedia fallback successful!")
                        return content
        except Exception as e2:
             print(f"Fallback failed: {e2}")

        print("Network/API error. Using DUMMY Wikipedia data for demonstration.")
        return f"{topic} is a highly successful franchise in the Indian Premier League (IPL). They have won 5 titles."

def generate_conversation_script(topic, context_text):
    """Generates a Hinglish conversation script using an LLM."""
    print("Generating Hinglish script...")
    
    system_prompt = """
    You are an expert scriptwriter for a viral Indian podcast. 
    Create a natural, high-energy conversation between two friends, Kabir (Host) and Ananya (Guest).
    
    Target Audience: Young Indians who speak mixed Hindi and English (Hinglish).
    Style: Conversational, informal, witty. NOT robotic.
    
    Rules:
    1. Language: Use natural Hinglish.
    2. Vocabulary: Use fillers like "Matlab", "Achcha", "Sahi mein?", "Bhai", "Umm...", "Hahaha".
    3. Emotion: MANDATORY: Include markers like "[laughs]", "[sighs]", "umm...", "phew".
    4. STRICT DURATION: The total length MUST be between 8 to 10 dialogue turns total (approx 150-180 words). This is crucial to keep the audio under 2 minutes.
    5. Content: Based on the provided context, but make it sound like a chat, not a lecture.
    
    Format: Return ONLY valid JSON in this exact structure:
    {
        "conversation": [
            {"speaker": "Kabir", "text": "Arre welcome back folks! [laughs]..."},
            {"speaker": "Ananya", "text": "..."},
            ...
        ]
    }
    """
    
    user_prompt = f"Topic: {topic}\n\nContext Info:\n{context_text}"
    
    try:
        if "sk-dummy" in client.api_key:
            raise Exception("Dummy key detected")

        response = client.chat.completions.create(
            model="gpt-4o",  # or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error generating script: {e}")
        print("Using DUMMY script for demonstration.")
        return {
            "conversation": [
                {"speaker": "Kabir", "text": f"Namaste doston! Aaj hum baat karenge {topic} ke baare mein."},
                {"speaker": "Ananya", "text": "Arre waah! {topic}? Yeh toh hot topic hai yaar!"},
                {"speaker": "Kabir", "text": "Bilkul! Suna hai maamla garam hai. IPL kings hain yeh log."},
                {"speaker": "Ananya", "text": "Haha, sahi kaha. Mumbai ka magic hi alag hai boss."},
                {"speaker": "Kabir", "text": "Chalo let's dive deep via this demo script!"}
            ]
        }

def text_to_speech_openai(script_json, output_file="hinglish_podcast.mp3"):
    """
    Converts the script to audio using GPT-4o Audio for natural Indian accents.
    """
    print("Converting script to audio using GPT-4o Audio (Human-like Indian Accent)...")
    
    combined_audio = b""
    # GPT-4o voices: alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer
    # Selection for Hinglish: 
    # Kabir -> 'ballad' (Warm, deep, Indian friendly)
    # Ananya -> 'coral' (Energetic, focused)
    voice_map = {"Kabir": "ballad", "Ananya": "coral"}
    
    dialogue = script_json.get("conversation", []) if isinstance(script_json, dict) else script_json
    if not isinstance(dialogue, list):
         if isinstance(script_json, dict):
             for v in script_json.values():
                 if isinstance(v, list):
                     dialogue = v
                     break
    
    try:
        if "sk-dummy" in client.api_key:
             raise Exception("Dummy key detected")
             
        import base64
        
        for line in dialogue:
            speaker = line.get("speaker", "Kabir")
            text = line.get("text", "")
            if not text: continue
            
            voice = voice_map.get(speaker, "ash")
            print(f"Generating human-like audio for {speaker}...")
            
            # Using gpt-4o-mini-audio-preview for cost-effective expressive speech
            response = client.chat.completions.create(
                model="gpt-4o-mini-audio-preview",
                modalities=["text", "audio"],
                audio={"voice": voice, "format": "mp3"},
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are {speaker}, an Indian person speaking Hinglish. Use a natural, expressive Indian accent. Include natural breathing and slight pauses where appropriate. Do not sound robotic."
                    },
                    {
                        "role": "user", 
                        "content": text
                    }
                ]
            )
            
            # The audio data is returned as base64 in the response
            audio_data = base64.b64decode(response.choices[0].message.audio.data)
            combined_audio += audio_data
            
        with open(output_file, "wb") as f:
            f.write(combined_audio)
        print(f"Human-like Hinglish Audio saved to {output_file}")
            
    except Exception as e:
        print(f"Error in GPT-4o Audio generation: {e}")
        # Fallback to local dummy if everything fails
        if not combined_audio:
            with open(output_file, "wb") as f:
                f.write(b'\xFF\xF3\x44\xC4' * 100)
            print(f"Dummy Audio saved to {output_file}")

def main():
    topic = input("Enter a topic (e.g., 'Mumbai Indians'): ") or "Mumbai Indians"
    
    # 1. Get Content
    wiki_text = get_wikipedia_content(topic)
    if not wiki_text:
        print("Topic not found on Wikipedia.")
        return

    # 2. Get Script
    script = generate_conversation_script(topic, wiki_text)
    
    # Save script for review
    with open("script.json", "w") as f:
        json.dump(script, f, indent=2)
    print("Script saved to script.json")
    
    # 3. Generate Audio
    text_to_speech_openai(script, "hinglish_podcast.mp3")

if __name__ == "__main__":
    main()
