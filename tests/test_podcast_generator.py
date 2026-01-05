import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Ensure the parent directory is in path so we can import the script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from podcast_generator import get_wikipedia_content, generate_conversation_script, text_to_speech_openai

class TestPodcastGenerator(unittest.TestCase):

    @patch('wikipediaapi.Wikipedia')
    def test_get_wikipedia_content_success(self, mock_wiki):
        """Test successful Wikipedia content retrieval."""
        mock_page = MagicMock()
        mock_page.exists.return_value = True
        mock_page.summary = "This is a test summary."
        
        mock_instance = MagicMock()
        mock_instance.page.return_value = mock_page
        mock_wiki.return_value = mock_instance
        
        content = get_wikipedia_content("Test Topic")
        self.assertEqual(content, "This is a test summary.")

    @patch('wikipediaapi.Wikipedia')
    @patch('requests.get')
    def test_get_wikipedia_content_fallback(self, mock_requests_get, mock_wiki):
        """Test fallback to raw requests when Wikipedia API fails (e.g. SSL error)."""
        # Force Wikipedia API to raise an exception
        mock_wiki.side_effect = Exception("SSL Error")
        
        # Mock requests fallback response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "123": {"extract": "Fallback content extracted."}
                }
            }
        }
        mock_requests_get.return_value = mock_response
        
        content = get_wikipedia_content("Mumbai Indians")
        self.assertIn("Fallback", content)

    @patch('podcast_generator.client.chat.completions.create')
    def test_generate_conversation_script_success(self, mock_openai):
        """Test successful script generation from LLM."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "conversation": [
                {"speaker": "Kabir", "text": "Hello"},
                {"speaker": "Ananya", "text": "Hi"}
            ]
        })
        mock_openai.return_value = mock_response
        
        # Ensure client.api_key is not dummy for this test
        with patch('podcast_generator.client.api_key', 'sk-valid-key'):
            script = generate_conversation_script("Topic", "Context")
            self.assertIn("conversation", script)
            self.assertEqual(len(script["conversation"]), 2)

    def test_generate_conversation_script_dummy_fallback(self):
        """Test dummy script fallback when API key is missing/dummy."""
        # The script is designed to raise an exception or return dummy if sk-dummy is present
        with patch('podcast_generator.client.api_key', 'sk-dummy-key'):
            script = generate_conversation_script("Mumbai Indians", "Some context")
            self.assertIn("conversation", script)
            self.assertEqual(script["conversation"][0]["speaker"], "Kabir")
            self.assertIn("Namaste", script["conversation"][0]["text"])

    @patch('podcast_generator.client.chat.completions.create')
    def test_text_to_speech_openai_success(self, mock_openai_audio):
        """Test successful audio generation (mocking OpenAI Audio preview)."""
        import base64
        fake_audio_content = b"fake-audio-bytes"
        encoded_audio = base64.b64encode(fake_audio_content).decode('utf-8')
        
        mock_response = MagicMock()
        mock_response.choices[0].message.audio.data = encoded_audio
        mock_openai_audio.return_value = mock_response
        
        test_script = {
            "conversation": [{"speaker": "Kabir", "text": "Test line"}]
        }
        output_file = "test_output.mp3"
        
        try:
            text_to_speech_openai(test_script, output_file)
            self.assertTrue(os.path.exists(output_file))
            with open(output_file, 'rb') as f:
                self.assertEqual(f.read(), fake_audio_content)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_text_to_speech_dummy_fallback(self):
        """Test dummy audio file creation when API fails."""
        with patch('podcast_generator.client.api_key', 'sk-dummy-key'):
            output_file = "dummy_test.mp3"
            try:
                text_to_speech_openai({}, output_file)
                self.assertTrue(os.path.exists(output_file))
                self.assertGreater(os.path.getsize(output_file), 0)
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)

if __name__ == '__main__':
    unittest.main()
