"""
LLM Engine for intelligent conversational responses
Supports Ollama, OpenAI, and Anthropic
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any
from config import LLM_CONFIG

logger = logging.getLogger(__name__)

class LLMEngine:
    """
    LLM Engine for generating intelligent conversational responses
    """
    
    def __init__(self, provider='ollama', model_name=None, **kwargs):
        """
        Initialize the LLM engine
        
        Args:
            provider (str): LLM provider ('ollama', 'openai', 'anthropic')
            model_name (str): Model name to use
            **kwargs: Additional provider-specific configuration
        """
        self.provider = provider.lower()
        self.model_name = model_name or LLM_CONFIG.get(f'{self.provider}_model', 'llama2')
        self.conversation_history = []
        self.max_history = LLM_CONFIG.get('max_conversation_history', 10)
        
        # Provider-specific configuration
        if self.provider == 'ollama':
            self.ollama_base_url = kwargs.get('base_url', 'http://localhost:11434')
        elif self.provider == 'openai':
            self.openai_api_key = kwargs.get('api_key', LLM_CONFIG.get('openai_api_key'))
            self.openai_base_url = kwargs.get('base_url', LLM_CONFIG.get('openai_base_url'))
        elif self.provider == 'anthropic':
            self.anthropic_api_key = kwargs.get('api_key', LLM_CONFIG.get('anthropic_api_key'))
        
        logger.info(f"LLM Engine initialized with provider: {self.provider}, model: {self.model_name}")
    
    def add_to_conversation(self, role: str, content: str):
        """
        Add a message to the conversation history
        
        Args:
            role (str): Role of the message ('user' or 'assistant')
            content (str): Content of the message
        """
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': time.time()
        })
        
        # Keep only the most recent messages
        if len(self.conversation_history) > self.max_history * 2:  # *2 because each exchange has 2 messages
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """
        Get formatted conversation context for LLM
        
        Returns:
            List of conversation messages in the format expected by the LLM
        """
        # Format conversation history for the specific provider
        if self.provider == 'ollama':
            # Ollama uses a simple format
            context = []
            for msg in self.conversation_history[-self.max_history * 2:]:
                context.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            return context
        else:
            # OpenAI/Anthropic use standard format
            return [{'role': msg['role'], 'content': msg['content']} 
                   for msg in self.conversation_history[-self.max_history * 2:]]
    
    def generate_response(self, user_message: str, system_prompt: str = None) -> str:
        """
        Generate a response to the user message
        
        Args:
            user_message (str): The user's message
            system_prompt (str): Optional system prompt to guide the response
            
        Returns:
            str: Generated response from the LLM
        """
        try:
            # Add user message to conversation
            self.add_to_conversation('user', user_message)
            
            # Generate response based on provider
            if self.provider == 'ollama':
                response = self._generate_ollama_response(user_message, system_prompt)
            elif self.provider == 'openai':
                response = self._generate_openai_response(user_message, system_prompt)
            elif self.provider == 'anthropic':
                response = self._generate_anthropic_response(user_message, system_prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Add assistant response to conversation
            self.add_to_conversation('assistant', response)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            error_response = f"I apologize, but I encountered an error: {str(e)}"
            self.add_to_conversation('assistant', error_response)
            return error_response
    
    def _generate_ollama_response(self, user_message: str, system_prompt: str = None) -> str:
        """Generate response using Ollama"""
        try:
            # Prepare the prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
            else:
                full_prompt = f"User: {user_message}\nAssistant:"
            
            # Add conversation context
            context = self.get_conversation_context()
            if len(context) > 2:  # More than just current exchange
                context_text = "\n".join([f"{msg['role'].title()}: {msg['content']}" 
                                        for msg in context[:-2]])  # Exclude current exchange
                full_prompt = f"{context_text}\n\n{full_prompt}"
            
            # Make request to Ollama
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    'model': self.model_name,
                    'prompt': full_prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'max_tokens': 200
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'I apologize, but I could not generate a response.')
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
    
    def _generate_openai_response(self, user_message: str, system_prompt: str = None) -> str:
        """Generate response using OpenAI"""
        try:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            import openai
            client = openai.OpenAI(
                api_key=self.openai_api_key,
                base_url=self.openai_base_url
            )
            
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            
            # Add conversation context
            context = self.get_conversation_context()
            messages.extend(context)
            
            # Add current user message
            messages.append({'role': 'user', 'content': user_message})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _generate_anthropic_response(self, user_message: str, system_prompt: str = None) -> str:
        """Generate response using Anthropic Claude"""
        try:
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({'role': 'user', 'content': f"System: {system_prompt}\n\nUser: {user_message}"})
            else:
                messages.append({'role': 'user', 'content': user_message})
            
            response = client.messages.create(
                model=self.model_name,
                max_tokens=500,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation"""
        return {
            'total_messages': len(self.conversation_history),
            'user_messages': len([m for m in self.conversation_history if m['role'] == 'user']),
            'assistant_messages': len([m for m in self.conversation_history if m['role'] == 'assistant']),
            'provider': self.provider,
            'model': self.model_name
        }
    
    def change_provider(self, new_provider: str, model_name: str = None, **kwargs):
        """
        Change the LLM provider
        
        Args:
            new_provider (str): New provider name
            model_name (str): New model name
            **kwargs: Additional configuration for the new provider
        """
        logger.info(f"Changing LLM provider from {self.provider} to {new_provider}")
        
        # Clear conversation when changing providers
        self.clear_conversation()
        
        # Reinitialize with new provider
        self.__init__(new_provider, model_name, **kwargs)

# Import time module at the top
import time
