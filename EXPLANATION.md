# Hinglish Prompting Strategy

To achieve authentic "Hinglish" conversation, I focused on three key areas in the prompt engineering:

1.  **Code-Switching Directives**: I explicitly instructed the LLM to use natural code-switching (mixing Hindi/English within sentences) rather than block translation. Keywords like "Arre yaar", "Sahi mein", and "Matlab" were mandated as mandatory fillers to break the "robotic" flow.

2.  **Persona Definition**: By assigning specific archetypes (Kabir as high-energy/enthusiastic, Ananya as witty/grounded), the dialogue gains natural conflict and rhythm.

3.  **Phonetic Cues**: I guided the model to include textual representations of speech dysfluencies (like "umm...", "phew") and laughter. While standard TTS engines read text literally, modern models like OpenAI's `tts-1` are trained to interpret these markers with surprising emotional inflection, bridging the gap between text and natural speech.
