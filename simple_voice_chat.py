"""
Simple Voice Chat Application - Manual start/stop transcription
"""

import logging
import numpy as np
import pyaudio
import threading
import time
import queue
from asr_engine import ASREngine

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleVoiceChat:
    """
    Simple voice chat application with manual transcription control
    """
    
    def __init__(self):
        """Initialize the voice chat application"""
        # Audio parameters
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        self.format_type = pyaudio.paInt16
        
        # Initialize ASR engine
        self.asr_engine = ASREngine(model_size='base', device='cpu')
        
        # Audio processing
        self.p = None
        self.stream = None
        self.is_running = False
        self.is_recording = False
        
        # Audio buffer
        self.audio_buffer = []
        
        # Threading
        self.audio_thread = None
        
        logger.info("Simple Voice Chat initialized")
    
    def start(self):
        """Start the voice chat application"""
        if self.is_running:
            logger.warning("Voice chat is already running")
            return
        
        try:
            # Initialize PyAudio
            self.p = pyaudio.PyAudio()
            logger.info("PyAudio initialized")
            
            # Open audio stream
            self.stream = self.p.open(
                format=self.format_type,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            logger.info("Audio stream opened")
            
            # Start processing
            self.is_running = True
            
            # Start audio capture thread
            self.audio_thread = threading.Thread(target=self._audio_capture_worker, daemon=True)
            self.audio_thread.start()
            
            logger.info("Voice chat started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start voice chat: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the voice chat application"""
        logger.info("Stopping voice chat...")
        
        self.is_running = False
        self.is_recording = False
        
        # Stop audio stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            logger.info("Audio stream closed")
        
        # Terminate PyAudio
        if self.p:
            self.p.terminate()
            logger.info("PyAudio terminated")
        
        logger.info("Voice chat stopped")
    
    def start_recording(self):
        """Start recording audio for transcription"""
        if not self.is_running:
            print("❌ Voice chat is not running. Start it first with .start()")
            return
        
        if self.is_recording:
            print("⚠️  Already recording!")
            return
        
        self.is_recording = True
        self.audio_buffer = []
        print("🎙️  Recording started... Speak now!")
        logger.info("Recording started")
    
    def stop_recording(self):
        """Stop recording and transcribe the audio"""
        if not self.is_recording:
            print("⚠️  Not currently recording!")
            return
        
        self.is_recording = False
        print("⏹️  Recording stopped. Transcribing...")
        logger.info("Recording stopped, processing audio")
        
        # Process the recorded audio
        self._process_audio_buffer()
    
    def _audio_capture_worker(self):
        """Audio capture worker thread"""
        logger.info("Audio capture worker started")
        
        while self.is_running:
            try:
                # Read audio data
                audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Convert to numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Add to buffer only if recording
                if self.is_recording:
                    self.audio_buffer.extend(audio_array)
                
            except Exception as e:
                logger.error(f"Error in audio capture: {e}")
                break
        
        logger.info("Audio capture worker stopped")
    
    def _process_audio_buffer(self):
        """Process the collected audio buffer"""
        if not self.audio_buffer:
            print("🔇 No audio recorded!")
            return
        
        try:
            # Convert to numpy array
            audio_array = np.array(self.audio_buffer, dtype=np.int16)
            
            # Convert to float32 and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Calculate duration
            duration = len(audio_float) / self.sample_rate
            print(f"📊 Audio duration: {duration:.1f} seconds")
            
            # Transcribe audio
            logger.info("Transcribing audio...")
            result = self.asr_engine.transcribe_audio(audio_float)
            
            if result['text'].strip():
                logger.info(f"Transcription: {result['text']}")
                print(f"\n🎤 Transcription: {result['text']}")
            else:
                logger.info("No speech detected")
                print("\n🔇 No speech detected in the recording")
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            print(f"❌ Error processing audio: {e}")

def main():
    """Main function to run the voice chat"""
    print("🎤 Simple Voice Chat Application - Manual Control")
    print("=" * 50)
    print("Commands:")
    print("  .start()     - Start the voice chat system")
    print("  .stop()      - Stop the voice chat system")
    print("  .record()    - Start recording audio")
    print("  .stoprec()   - Stop recording and transcribe")
    print("  .quit        - Exit the application")
    print()
    
    voice_chat = SimpleVoiceChat()
    
    try:
        while True:
            command = input("🎤 Enter command: ").strip().lower()
            
            if command == ".start":
                voice_chat.start()
                print("✅ Voice chat system started")
                
            elif command == ".stop":
                voice_chat.stop()
                print("✅ Voice chat system stopped")
                
            elif command == ".record":
                voice_chat.start_recording()
                
            elif command == ".stoprec":
                voice_chat.stop_recording()
                
            elif command == ".quit":
                print("👋 Goodbye!")
                break
                
            elif command == "help":
                print("Commands: .start, .stop, .record, .stoprec, .quit, help")
                
            else:
                print("❓ Unknown command. Type 'help' for available commands.")
                
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        if voice_chat.is_running:
            voice_chat.stop()

if __name__ == "__main__":
    main()
