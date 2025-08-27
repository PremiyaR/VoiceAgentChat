"""
Enhanced Voice Chat Application with LLM Integration
Provides intelligent conversational responses to audio transcriptions
"""

import logging
import numpy as np
import pyaudio
import threading
import time
import queue
from asr_engine import ASREngine
from llm_engine import LLMEngine
from config import LLM_CONFIG, AUDIO_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedVoiceChat:
    """
    Enhanced voice chat application with LLM integration for intelligent responses
    """
    
    def __init__(self, llm_provider='ollama', llm_model=None):
        """
        Initialize the enhanced voice chat application
        
        Args:
            llm_provider (str): LLM provider ('ollama', 'openai', 'anthropic')
            llm_model (str): Specific model to use
        """
        # Audio parameters
        self.sample_rate = AUDIO_CONFIG['sample_rate']
        self.chunk_size = AUDIO_CONFIG['chunk_size']
        self.channels = AUDIO_CONFIG['channels']
        self.format_type = pyaudio.paInt16
        
        # Initialize ASR engine
        self.asr_engine = ASREngine(model_size='base', device='cpu')
        
        # Initialize LLM engine
        self.llm_engine = LLMEngine(
            provider=llm_provider,
            model_name=llm_model,
            base_url=LLM_CONFIG.get('ollama_base_url'),
            api_key=LLM_CONFIG.get(f'{llm_provider}_api_key')
        )
        
        # Audio processing
        self.p = None
        self.stream = None
        self.is_running = False
        self.is_recording = False
        
        # Audio buffer
        self.audio_buffer = []
        
        # Threading
        self.audio_thread = None
        
        # Conversation state
        self.conversation_active = False
        self.system_prompt = LLM_CONFIG.get('system_prompt')
        
        logger.info(f"Enhanced Voice Chat initialized with {llm_provider} LLM")
    
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
            
            logger.info("Enhanced voice chat started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start voice chat: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the voice chat application"""
        logger.info("Stopping enhanced voice chat...")
        
        self.is_running = False
        self.is_recording = False
        self.conversation_active = False
        
        # Stop audio stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            logger.info("Audio stream closed")
        
        # Terminate PyAudio
        if self.p:
            self.p.terminate()
            logger.info("PyAudio terminated")
        
        logger.info("Enhanced voice chat stopped")
    
    def start_conversation(self):
        """Start an interactive conversation session"""
        if not self.is_running:
            print("❌ Voice chat is not running. Start it first with .start()")
            return
        
        if self.conversation_active:
            print("⚠️  Conversation already active!")
            return
        
        self.conversation_active = True
        print("🤖 Starting intelligent conversation mode...")
        print("💡 The AI will now respond to your transcribed speech!")
        print("🎙️  Use .record() to speak, .stoprec() to get AI response")
        print("🔄 Use .newtopic() to start a new conversation topic")
        print("📝 Use .history() to see conversation history")
        print("❌ Use .endconv() to end the conversation")
        logger.info("Conversation mode activated")
    
    def end_conversation(self):
        """End the current conversation session"""
        if not self.conversation_active:
            print("⚠️  No active conversation to end!")
            return
        
        self.conversation_active = False
        print("🤖 Conversation mode deactivated")
        logger.info("Conversation mode deactivated")
    
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
        """Stop recording and process the audio with LLM response"""
        if not self.is_recording:
            print("⚠️  Not currently recording!")
            return
        
        self.is_recording = False
        print("⏹️  Recording stopped. Processing...")
        logger.info("Recording stopped, processing audio")
        
        # Process the recorded audio
        self._process_audio_with_llm()
    
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
    
    def _process_audio_with_llm(self):
        """Process the collected audio buffer and generate LLM response"""
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
                user_message = result['text'].strip()
                logger.info(f"Transcription: {user_message}")
                print(f"\n🎤 You said: {user_message}")
                
                # Generate LLM response if conversation is active
                if self.conversation_active:
                    print("🤖 Generating AI response...")
                    try:
                        ai_response = self.llm_engine.generate_response(
                            user_message, 
                            self.system_prompt
                        )
                        print(f"\n🤖 AI Response: {ai_response}")
                        logger.info("LLM response generated successfully")
                    except Exception as e:
                        error_msg = f"Failed to generate AI response: {str(e)}"
                        print(f"\n❌ {error_msg}")
                        logger.error(error_msg)
                else:
                    print("💡 Use .startconv() to begin an AI conversation!")
                    
            else:
                logger.info("No speech detected")
                print("\n🔇 No speech detected in the recording")
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            print(f"❌ Error processing audio: {e}")
    
    def new_topic(self):
        """Start a new conversation topic"""
        if not self.conversation_active:
            print("❌ Start a conversation first with .startconv()")
            return
        
        self.llm_engine.clear_conversation()
        print("🔄 New conversation topic started!")
        logger.info("New conversation topic started")
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_active:
            print("❌ No active conversation to show history for")
            return
        
        summary = self.llm_engine.get_conversation_summary()
        print(f"\n📝 Conversation Summary:")
        print(f"   Total messages: {summary['total_messages']}")
        print(f"   Your messages: {summary['user_messages']}")
        print(f"   AI responses: {summary['assistant_messages']}")
        print(f"   LLM Provider: {summary['provider']}")
        print(f"   Model: {summary['model']}")
        
        if summary['total_messages'] > 0:
            print(f"\n🔄 Recent conversation:")
            for i, msg in enumerate(self.llm_engine.conversation_history[-6:], 1):
                role_emoji = "👤" if msg['role'] == 'user' else "🤖"
                print(f"   {i}. {role_emoji} {msg['role'].title()}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
    
    def change_llm(self, provider, model=None):
        """Change the LLM provider and model"""
        try:
            self.llm_engine.change_provider(provider, model)
            print(f"✅ LLM changed to {provider} with model {self.llm_engine.model_name}")
            logger.info(f"LLM provider changed to {provider}")
        except Exception as e:
            print(f"❌ Failed to change LLM: {e}")
            logger.error(f"Failed to change LLM provider: {e}")
    
    def get_status(self):
        """Get current application status"""
        status = {
            'running': self.is_running,
            'recording': self.is_recording,
            'conversation_active': self.conversation_active,
            'llm_provider': self.llm_engine.provider,
            'llm_model': self.llm_engine.model_name,
            'conversation_length': len(self.llm_engine.conversation_history)
        }
        
        print(f"\n📊 Application Status:")
        print(f"   Voice Chat: {'🟢 Running' if status['running'] else '🔴 Stopped'}")
        print(f"   Recording: {'🔴 Recording' if status['recording'] else '⚪ Idle'}")
        print(f"   Conversation: {'🟢 Active' if status['conversation_active'] else '⚪ Inactive'}")
        print(f"   LLM Provider: {status['llm_provider']}")
        print(f"   LLM Model: {status['llm_model']}")
        print(f"   Messages in Memory: {status['conversation_length']}")
        
        return status

def main():
    """Main function to run the enhanced voice chat"""
    print("🤖 Enhanced Voice Chat with AI Intelligence")
    print("=" * 60)
    print("Features:")
    print("  • Speech-to-Text transcription")
    print("  • AI-powered conversational responses")
    print("  • Multiple LLM providers (Ollama, OpenAI, Anthropic)")
    print("  • Conversation memory and context")
    print()
    print("Commands:")
    print("  .start()      - Start the voice chat system")
    print("  .stop()       - Stop the voice chat system")
    print("  .startconv()  - Start AI conversation mode")
    print("  .endconv()    - End AI conversation mode")
    print("  .record()     - Start recording audio")
    print("  .stoprec()    - Stop recording and get AI response")
    print("  .newtopic()   - Start new conversation topic")
    print("  .history()    - Show conversation history")
    print("  .status()     - Show application status")
    print("  .change_llm() - Change LLM provider/model")
    print("  .quit         - Exit the application")
    print()
    
    voice_chat = EnhancedVoiceChat()
    
    try:
        while True:
            command = input("🤖 Enter command: ").strip().lower()
            
            if command == ".start":
                voice_chat.start()
                print("✅ Enhanced voice chat system started")
                
            elif command == ".stop":
                voice_chat.stop()
                print("✅ Enhanced voice chat system stopped")
                
            elif command == ".startconv":
                voice_chat.start_conversation()
                
            elif command == ".endconv":
                voice_chat.end_conversation()
                
            elif command == ".record":
                voice_chat.start_recording()
                
            elif command == ".stoprec":
                voice_chat.stop_recording()
                
            elif command == ".newtopic":
                voice_chat.new_topic()
                
            elif command == ".history":
                voice_chat.show_history()
                
            elif command == ".status":
                voice_chat.get_status()
                
            elif command == ".change_llm":
                print("Available providers: ollama, openai, anthropic")
                provider = input("Enter provider: ").strip().lower()
                model = input("Enter model name (or press Enter for default): ").strip() or None
                voice_chat.change_llm(provider, model)
                
            elif command == ".quit":
                print("👋 Goodbye!")
                break
                
            elif command == "help":
                print("Commands: .start, .stop, .startconv, .endconv, .record, .stoprec, .newtopic, .history, .status, .change_llm, .quit, help")
                
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
