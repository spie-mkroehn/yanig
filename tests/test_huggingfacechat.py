import unittest
from unittest.mock import patch, MagicMock
import sys
import json
import os


# Add the parent directory to the path so we can import the functions module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.huggingfacechat import HuggingFaceChat


class TestHuggingFaceChat(unittest.TestCase):
    
    def setUp(self):
        # Set up environment variable for testing
        os.environ["HUGGINGFACE_API_TOKEN"] = "test_token"
        
        # Create an instance of HuggingFaceChat with default settings
        self.hf_chat = HuggingFaceChat()
        
        # Sample chat history for testing
        self.sample_history = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        # Expected formatted messages
        self.expected_formatted_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        # Mock response from Hugging Face API
        self.mock_response = MagicMock()
        self.mock_response.choices = [
            MagicMock(message=MagicMock(content="I am doing well, thank you for asking!"))
        ]
    
    @patch("huggingface_hub.InferenceClient")
    def test_invoke_with_default_model(self, mock_inference_client):
        # Set up the mock
        mock_client_instance = mock_inference_client.return_value
        mock_client_instance.chat_completion.return_value = self.mock_response
        
        # Call the invoke method
        result = self.hf_chat.invoke(self.sample_history)
        
        # Verify InferenceClient was initialized with the correct token
        mock_inference_client.assert_called_once_with(token="test_token")
        
        # Verify chat_completion was called with the correct parameters
        mock_client_instance.chat_completion.assert_called_once_with(
            model="mistralai/Mistral-7B-Instruct-v0.3",  # Default model
            messages=self.expected_formatted_messages,
            temperature=0.0,
            stream=False
        )
        
        # Verify the result is as expected
        self.assertEqual(result, "I am doing well, thank you for asking!")
    
    @patch("huggingface_hub.InferenceClient")
    def test_invoke_with_custom_model(self, mock_inference_client):
        # Create an instance with a custom model
        custom_model = "meta-llama/Llama-2-70b-chat-hf"
        custom_temp = 0.7
        hf_chat_custom = HuggingFaceChat(language_model=custom_model, temperature=custom_temp)
        
        # Set up the mock
        mock_client_instance = mock_inference_client.return_value
        mock_client_instance.chat_completion.return_value = self.mock_response
        
        # Call the invoke method
        result = hf_chat_custom.invoke(self.sample_history)
        
        # Verify InferenceClient was initialized with the correct token
        mock_inference_client.assert_called_once_with(token="test_token")
        
        # Verify chat_completion was called with the correct parameters
        mock_client_instance.chat_completion.assert_called_once_with(
            model=custom_model,
            messages=self.expected_formatted_messages,
            temperature=custom_temp,
            stream=False
        )
        
        # Verify the result is as expected
        self.assertEqual(result, "I am doing well, thank you for asking!")


if __name__ == "__main__":
    unittest.main()
