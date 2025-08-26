"""
ASR Engine using faster-whisper
"""

import logging
import numpy as np
from faster_whisper import WhisperModel
from config import WHISPER_CONFIG

logger = logging.getLogger(__name__)

class ASREngine:
    """
    Automatic Speech Recognition engine using faster-whisper
    """
    
    def __init__(self, model_size=None, device=None, compute_type=None):
        """
        Initialize the ASR engine
        
        Args:
            model_size (str): Whisper model size (tiny, base, small, medium, large)
            device (str): Device to use (cpu, cuda, auto)
            compute_type (str): Compute type (int8, int16, float16, float32)
        """
        self.model_size = model_size or WHISPER_CONFIG['model_size']
        self.device = device or WHISPER_CONFIG['device']
        self.compute_type = compute_type or WHISPER_CONFIG['compute_type']
        
        logger.info(f"Initializing ASR engine with model: {self.model_size}")
        
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("ASR engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ASR engine: {e}")
            raise
    
    def transcribe_audio(self, audio_data, language=None):
        """
        Transcribe audio data to text
        
        Args:
            audio_data (numpy.ndarray): Audio data as numpy array
            language (str): Language code (None for auto-detection)
            
        Returns:
            dict: Transcription result with text and metadata
        """
        try:
            # Ensure audio data is in the correct format
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize audio if needed
            if np.max(np.abs(audio_data)) > 1.0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Transcribe using faster-whisper
            segments, info = self.model.transcribe(
                audio_data,
                language=language or WHISPER_CONFIG['language'],
                beam_size=WHISPER_CONFIG['beam_size'],
                best_of=WHISPER_CONFIG['best_of'],
                temperature=WHISPER_CONFIG['temperature'],
                compression_ratio_threshold=WHISPER_CONFIG['compression_ratio_threshold'],
                log_prob_threshold=WHISPER_CONFIG['log_prob_threshold'],
                no_speech_threshold=WHISPER_CONFIG['no_speech_threshold'],
                condition_on_previous_text=WHISPER_CONFIG['condition_on_previous_text'],
                initial_prompt=WHISPER_CONFIG['initial_prompt'],
                word_timestamps=WHISPER_CONFIG['word_timestamps'],
                prepend_punctuations=WHISPER_CONFIG['prepend_punctuations'],
                append_punctuations=WHISPER_CONFIG['append_punctuations']
            )
            
            # Process segments
            transcription_text = ""
            segments_list = []
            
            for segment in segments:
                transcription_text += segment.text + " "
                segments_list.append({
                    'text': segment.text,
                    'start': segment.start,
                    'end': segment.end,
                    'words': segment.words if segment.words else []
                })
            
            result = {
                'text': transcription_text.strip(),
                'segments': segments_list,
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration
            }
            
            logger.info(f"Transcription completed: {len(transcription_text)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                'text': "",
                'segments': [],
                'language': None,
                'language_probability': 0.0,
                'duration': 0.0,
                'error': str(e)
            }
    
    def transcribe_file(self, audio_file_path, language=None):
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path (str): Path to audio file
            language (str): Language code (None for auto-detection)
            
        Returns:
            dict: Transcription result with text and metadata
        """
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            # Transcribe using faster-whisper
            segments, info = self.model.transcribe(
                audio_file_path,
                language=language or WHISPER_CONFIG['language'],
                beam_size=WHISPER_CONFIG['beam_size'],
                best_of=WHISPER_CONFIG['best_of'],
                temperature=WHISPER_CONFIG['temperature'],
                compression_ratio_threshold=WHISPER_CONFIG['compression_ratio_threshold'],
                log_prob_threshold=WHISPER_CONFIG['log_prob_threshold'],
                no_speech_threshold=WHISPER_CONFIG['no_speech_threshold'],
                condition_on_previous_text=WHISPER_CONFIG['condition_on_previous_text'],
                initial_prompt=WHISPER_CONFIG['initial_prompt'],
                word_timestamps=WHISPER_CONFIG['word_timestamps'],
                prepend_punctuations=WHISPER_CONFIG['prepend_punctuations'],
                append_punctuations=WHISPER_CONFIG['append_punctuations']
            )
            
            # Process segments
            transcription_text = ""
            segments_list = []
            
            for segment in segments:
                transcription_text += segment.text + " "
                segments_list.append({
                    'text': segment.text,
                    'start': segment.start,
                    'end': segment.end,
                    'words': segment.words if segment.words else []
                })
            
            result = {
                'text': transcription_text.strip(),
                'segments': segments_list,
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration
            }
            
            logger.info(f"File transcription completed: {len(transcription_text)} characters")
            return result
            
        except Exception as e:
            logger.error(f"File transcription failed: {e}")
            return {
                'text': "",
                'segments': [],
                'language': None,
                'language_probability': 0.0,
                'duration': 0.0,
                'error': str(e)
            }
    
    def get_available_models(self):
        """
        Get list of available model sizes
        
        Returns:
            list: Available model sizes
        """
        return ['tiny', 'base', 'small', 'medium', 'large']
    
    def change_model(self, model_size):
        """
        Change the Whisper model
        
        Args:
            model_size (str): New model size
        """
        if model_size not in self.get_available_models():
            raise ValueError(f"Invalid model size: {model_size}")
        
        logger.info(f"Changing model to: {model_size}")
        
        try:
            self.model = WhisperModel(
                model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            self.model_size = model_size
            logger.info(f"Model changed successfully to: {model_size}")
        except Exception as e:
            logger.error(f"Failed to change model: {e}")
            raise
