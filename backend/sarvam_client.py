import requests
import json
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class SarvamAPIClient:
    
    BASE_URL = "https://api.sarvam.ai/generate"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SARVAM_API_KEY')
        
        if not self.api_key:
            logger.warning(
                "Sarvam API key not found. Set SARVAM_API_KEY environment variable. "
                "Falling back to mock responses for demonstration."
            )
    
    def _get_api_key(self) -> Optional[str]:
        return os.getenv('SARVAM_API_KEY')
    
    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 200,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        
        if use_mock or not self.api_key:
            return self._generate_mock_response(prompt, temperature, max_tokens)
        
        try:
            response = self._call_sarvam_api(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                'success': True,
                'text': response.get('text', ''),
                'prompt_used': prompt,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'model': 'Sarvam-2B'
            }
            
        except Exception as e:
            logger.error(f"Sarvam API call failed: {str(e)}")
            logger.info("Falling back to mock response")
            return self._generate_mock_response(prompt, temperature, max_tokens)
    
    def _call_sarvam_api(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'input': prompt,
            'model_name': 'Sarvam-2B-Instruct-v0.1',
            'do_sample': True,
            'max_tokens': int(max_tokens),
            'temperature': float(temperature),
            'top_p': 0.95
        }
        
        response = requests.post(
            self.BASE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'text': data.get('generated_text', {}).get('output', '')
        }
    
    def _generate_mock_response(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        
        if temperature < 0.3:
            response_text = (
                "Thank you for contacting us. Based on our policies, "
                "your request has been processed according to the guidelines provided. "
                "Please allow 5-7 business days for the completion of your request."
            )
        elif temperature < 0.6:
            response_text = (
                "We appreciate your concern and have reviewed your issue. "
                "Based on our customer support guidelines, we are happy to assist you. "
                "We will process your request and keep you updated on the progress."
            )
        else:
            response_text = (
                "Thank you so much for reaching out to us! We completely understand your situation "
                "and really appreciate your patience. Our team is committed to making this right for you. "
                "We'll prioritize your request and follow up with you shortly!"
            )
        
        return {
            'success': True,
            'text': response_text,
            'prompt_used': prompt,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'model': 'Sarvam-2B (Mock)',
            'mock': True
        }
    
    @staticmethod
    def validate_parameters(temperature: float, max_tokens: int) -> bool:
        
        if not (0.0 <= temperature <= 1.0):
            logger.warning(f"Temperature {temperature} out of range [0, 1]")
            return False
        
        if not (1 <= max_tokens <= 2048):
            logger.warning(f"Max tokens {max_tokens} out of range [1, 2048]")
            return False
        
        return True
