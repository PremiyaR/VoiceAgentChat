"""
Configuration file for Simple Voice Chat Application
"""

# Audio Configuration
AUDIO_CONFIG = {
    'sample_rate': 16000,      # Sample rate in Hz
    'chunk_size': 1024,        # Audio chunk size
    'channels': 1,             # Mono audio
    'format': 'int16',         # Audio format
    'recording_duration': 5.0, # Recording duration in seconds
}

# Whisper Configuration
WHISPER_CONFIG = {
    'model_size': 'base',      # Model size: tiny, base, small, medium, large
    'device': 'auto',          # Device: cpu, cuda, auto
    'compute_type': 'auto',    # Compute type: int8, int16, float16, float32
    'language': None,          # Language code (None for auto-detection)
    'beam_size': 5,            # Beam size for beam search
    'best_of': 5,              # Number of candidates to consider
    'temperature': 0.0,        # Temperature for sampling
    'compression_ratio_threshold': 2.4,
    'log_prob_threshold': -1.0,
    'no_speech_threshold': 0.6,
    'condition_on_previous_text': True,
    'initial_prompt': None,
    'word_timestamps': False,
    'prepend_punctuations': "\"'([{-",
    'append_punctuations': "\"'.!?()[]{},:;",
}

# LLM Configuration
LLM_CONFIG = {
    # General LLM settings
    'default_provider': 'ollama',  # Default LLM provider
    'max_conversation_history': 10,  # Maximum conversation history to keep
    
    # Ollama settings
    'ollama_model': 'llama2',  # Default Ollama model
    'ollama_base_url': 'http://localhost:11434',  # Ollama server URL
    
    # OpenAI settings (optional)
    'openai_model': 'gpt-3.5-turbo',  # Default OpenAI model
    'openai_api_key': None,  # Set your OpenAI API key here
    'openai_base_url': 'https://api.openai.com/v1',  # OpenAI API base URL
    
    # Anthropic settings (optional)
    'anthropic_model': 'claude-3-haiku-20240307',  # Default Anthropic model
    'anthropic_api_key': None,  # Set your Anthropic API key here
    
    # System prompt for conversational AI
    'system_prompt': """You are a helpful, friendly, and intelligent conversational AI assistant. 
    You engage in natural conversations, provide helpful information, and respond appropriately to user queries. 
    Keep your responses conversational, concise, and engaging. If you don't know something, be honest about it."""
}
