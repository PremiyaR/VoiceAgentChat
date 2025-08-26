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
