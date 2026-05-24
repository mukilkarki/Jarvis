"""
voice_engine.py - Voice input/output engine for Gwen AI
"""

import os
import io
import asyncio
import tempfile
import threading
from typing import Optional, Callable

from utils.logger import gwen_logger


class VoiceEngine:
    """
    Voice engine for speech recognition and text-to-speech.
    Uses edge-tts for high-quality female voice with pyttsx3 fallback.
    """
    
    def __init__(self):
        """Initialize voice engine."""
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.listening = False
        self.speaking = False
        self.voice_enabled = True
        self._init_engines()
    
    def _init_engines(self):
        """Initialize speech recognition and TTS engines."""
        # Try to initialize speech recognition
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            gwen_logger.voice("Speech recognition initialized")
        except Exception as e:
            gwen_logger.warning(f"Speech recognition unavailable: {e}")
        
        # Try to initialize pyttsx3 as fallback TTS
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configure voice properties
            voices = self.tts_engine.getProperty('voices')
            # Try to find a female voice
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_engine.setProperty('rate', 180)  # Speed
            self.tts_engine.setProperty('volume', 0.9)
            gwen_logger.voice("pyttsx3 TTS engine initialized")
        except Exception as e:
            gwen_logger.warning(f"pyttsx3 unavailable: {e}")
    
    # ─── TEXT-TO-SPEECH ──────────────────────────────────────────────
    
    def speak(self, text: str, use_edge_tts: bool = True) -> bool:
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
            use_edge_tts: Try edge-tts first if available
        """
        if not self.voice_enabled:
            gwen_logger.voice("Voice output disabled")
            return False
        
        self.speaking = True
        
        try:
            if use_edge_tts:
                success = self._speak_edge_tts(text)
                if success:
                    return True
            
            # Fallback to pyttsx3
            return self._speak_pyttsx3(text)
        except Exception as e:
            gwen_logger.error(f"TTS failed: {e}")
            return False
        finally:
            self.speaking = False
    
    def _speak_edge_tts(self, text: str) -> bool:
        """Use edge-tts for high-quality female voice."""
        try:
            import edge_tts
            
            # Use a natural female voice
            voice = "en-US-JennyNeural"  # Microsoft Jenny - natural female voice
            
            async def _tts():
                communicate = edge_tts.Communicate(text, voice)
                # Play directly or save to temp file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    temp_path = f.name
                
                await communicate.save(temp_path)
                
                # Play the audio file
                try:
                    import playsound
                    playsound.playsound(temp_path, block=True)
                except Exception:
                    # Try alternative playback methods
                    import subprocess
                    subprocess.run(["ffplay", "-nodisp", "-autoexit", temp_path], 
                                 capture_output=True, timeout=30)
                
                # Cleanup
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            
            asyncio.run(_tts())
            return True
        except Exception as e:
            gwen_logger.debug(f"edge-tts failed: {e}")
            return False
    
    def _speak_pyttsx3(self, text: str) -> bool:
        """Use pyttsx3 for TTS (fallback)."""
        try:
            if self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                return True
            return False
        except Exception as e:
            gwen_logger.error(f"pyttsx3 TTS failed: {e}")
            return False
    
    def speak_async(self, text: str):
        """Speak text in a separate thread."""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()
    
    # ─── SPEECH RECOGNITION ──────────────────────────────────────────
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for a phrase
        
        Returns:
            Recognized text or None
        """
        if not self.recognizer:
            gwen_logger.voice("Speech recognition not available")
            return None
        
        try:
            import speech_recognition as sr
            
            with sr.Microphone() as source:
                gwen_logger.voice("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    gwen_logger.voice("Listening timeout")
                    return None
                
                gwen_logger.voice("Processing speech...")
                
                # Try multiple recognition engines
                text = None
                
                # Try Google Web Speech API first
                try:
                    text = self.recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    gwen_logger.voice("Could not understand audio")
                except sr.RequestError:
                    gwen_logger.voice("Speech recognition service unavailable")
                
                if text:
                    gwen_logger.voice(f"Recognized: {text}")
                    return text
                
                return None
                
        except Exception as e:
            gwen_logger.error(f"Microphone error: {e}")
            return None
    
    def listen_continuous(self, callback: Callable[[str], None], wake_word: Optional[str] = None):
        """
        Continuously listen for voice input.
        
        Args:
            callback: Function to call with recognized text
            wake_word: Optional wake word to trigger processing
        """
        self.listening = True
        
        while self.listening:
            try:
                text = self.listen(timeout=2, phrase_time_limit=5)
                
                if text and callback:
                    if wake_word:
                        # Check if wake word is in the text
                        if wake_word.lower() in text.lower():
                            # Remove wake word from text
                            cleaned = text.lower().replace(wake_word.lower(), "").strip()
                            if cleaned:
                                callback(cleaned)
                    else:
                        callback(text)
                        
            except Exception as e:
                gwen_logger.error(f"Continuous listening error: {e}")
                continue
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.listening = False
        gwen_logger.voice("Listening stopped")
    
    def toggle_voice(self) -> bool:
        """Toggle voice output on/off."""
        self.voice_enabled = not self.voice_enabled
        status = "enabled" if self.voice_enabled else "disabled"
        gwen_logger.voice(f"Voice output {status}")
        return self.voice_enabled


# Global voice engine instance
voice = VoiceEngine()