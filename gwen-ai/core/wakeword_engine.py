"""
wakeword_engine.py - Wake word detection engine for Gwen AI
"""

import os
import re
import time
import threading
from typing import Optional, Callable

from utils.logger import gwen_logger


class WakeWordEngine:
    """
    Wake word detection engine.
    Supports "Hey Gwen" and "Gwen" as wake words.
    Uses simple keyword spotting with speech recognition.
    """
    
    WAKE_WORDS = ["hey gwen", "gwen", "gwennie"]
    
    def __init__(self):
        """Initialize wake word engine."""
        self.listening = False
        self.thread = None
        self.callback: Optional[Callable] = None
        self.last_trigger_time = 0
        self.cooldown_seconds = 3  # Prevent multiple triggers
        
        gwen_logger.system("Wake word engine initialized")
    
    def start_listening(self, on_trigger: Callable):
        """
        Start listening for wake words.
        
        Args:
            on_trigger: Callback when wake word is detected
        """
        self.callback = on_trigger
        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        gwen_logger.system("Wake word listening started")
    
    def stop_listening(self):
        """Stop wake word detection."""
        self.listening = False
        gwen_logger.system("Wake word listening stopped")
    
    def _listen_loop(self):
        """Background loop for wake word detection."""
        while self.listening:
            try:
                self._check_for_wake_word()
                time.sleep(0.5)  # Check every 500ms
            except Exception as e:
                gwen_logger.debug(f"Wake word check error: {e}")
                time.sleep(1)
    
    def _check_for_wake_word(self):
        """Check if wake word was spoken using speech recognition."""
        try:
            import speech_recognition as sr
            
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                recognizer.energy_threshold = 300
                recognizer.dynamic_energy_threshold = True
                recognizer.pause_threshold = 0.8
                
                try:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                except sr.WaitTimeoutError:
                    return
                
                try:
                    text = recognizer.recognize_google(audio).lower()
                    
                    # Check for wake words
                    for wake_word in self.WAKE_WORDS:
                        if wake_word in text:
                            # Check cooldown
                            current_time = time.time()
                            if current_time - self.last_trigger_time > self.cooldown_seconds:
                                self.last_trigger_time = current_time
                                
                                gwen_logger.voice(f"Wake word detected: '{wake_word}'")
                                
                                # Extract command after wake word
                                command = text.replace(wake_word, "").strip()
                                
                                if self.callback:
                                    self.callback(command if command else None)
                                return
                                
                except (sr.UnknownValueError, sr.RequestError):
                    pass
                    
        except Exception as e:
            gwen_logger.debug(f"Wake word detection failed: {e}")
    
    def is_wake_word(self, text: str) -> bool:
        """Check if text contains a wake word."""
        text_lower = text.lower().strip()
        for wake_word in self.WAKE_WORDS:
            if text_lower.startswith(wake_word) or text_lower == wake_word:
                return True
        return False
    
    def extract_command(self, text: str) -> Optional[str]:
        """Extract the command portion after the wake word."""
        text_lower = text.lower().strip()
        
        for wake_word in self.WAKE_WORDS:
            if text_lower.startswith(wake_word):
                command = text[len(wake_word):].strip()
                return command if command else None
            
        return text if not self.is_wake_word(text) else None


# Global wake word engine instance
wakeword = WakeWordEngine()