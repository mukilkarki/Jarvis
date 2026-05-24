"""
main.py - Gwen AI Main Entry Point
====================================
Futuristic personal Jarvis-style AI assistant with voice interaction,
memory, productivity system, automation, and emotional intelligence.
"""

import os
import sys
import time
import random
import threading
from datetime import datetime
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import gwen_logger, COLORS
from utils.helpers import load_json, save_json, get_time_greeting
from utils.parser import CommandParser
from core.ai_engine import ai_engine
from core.voice_engine import voice
from core.memory_engine import memory
from core.automation_engine import automation
from core.emotion_engine import emotion_engine
from core.productivity_engine import productivity
from core.notification_engine import notifications
from core.wakeword_engine import wakeword
from core.command_engine import command_engine
from firebase.firebase_config import load_env_file


class GwenAI:
    """
    Main Gwen AI application class.
    Coordinates all engines and provides the user interface.
    """
    
    VERSION = "1.0.0"
    APP_NAME = "GWEN AI"
    
    def __init__(self):
        """Initialize Gwen AI system."""
        self.running = False
        self.input_mode = "text"  # 'text' or 'voice'
        self.parser = CommandParser()
        
        # Load environment
        load_env_file()
        
        # Configure API key from environment
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if api_key:
            ai_engine.set_api_key(api_key)
        
        # Model selection
        model = os.getenv("OPENROUTER_MODEL", "deepseek")
        ai_engine.set_model(model)
    
    # ─── STARTUP SEQUENCE ───────────────────────────────────────────
    
    def start(self):
        """Start the Gwen AI system."""
        self.running = True
        
        # Display startup sequence
        self._show_startup()
        
        # Start notification scheduler
        notifications.start()
        
        # Start wake word detection
        self._start_wakeword()
        
        # Main interaction loop
        self._main_loop()
    
    def _show_startup(self):
        """Display futuristic startup animation."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # ASCII Art Banner
        banner = f"""
{COLORS['CYAN']}{COLORS['BOLD']}
        ██████╗ ██╗    ██╗███████╗███╗   ██╗
       ██╔════╝ ██║    ██║██╔════╝████╗  ██║
       ██║  ███╗██║ █╗ ██║█████╗  ██╔██╗ ██║
       ██║   ██║██║███╗██║██╔══╝  ██║╚██╗██║
       ╚██████╔╝╚███╔███╔╝███████╗██║ ╚████║
        ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═══╝
{COLORS['RESET']}
{COLORS['MAGENTA']}{COLORS['BOLD']}            A I   A S S I S T A N T{COLORS['RESET']}
        """
        print(banner)
        
        # Loading animation
        loading_texts = [
            "Initializing neural networks...",
            "Loading personality matrix...",
            "Syncing memory banks...",
            "Calibrating voice engine...",
            "Establishing AI consciousness...",
            "Activating Gwen AI system..."
        ]
        
        for text in loading_texts:
            print(f"{COLORS['DIM']}{COLORS['CYAN']}  ⚡ {text}{COLORS['RESET']}")
            time.sleep(0.3)
        
        # System info
        print(f"\n{COLORS['GREEN']}{COLORS['BOLD']}  ✅ System initialized successfully!{COLORS['RESET']}")
        print(f"{COLORS['DIM']}  ─────────────────────────────────────────{COLORS['RESET']}")
        print(f"  {COLORS['CYAN']}Version:{COLORS['RESET']} {self.VERSION}")
        
        # Check API key status
        if ai_engine.api_key:
            print(f"  {COLORS['GREEN']}✓ OpenRouter API:{COLORS['RESET']} Connected")
            print(f"  {COLORS['CYAN']}Model:{COLORS['RESET']} {ai_engine.current_model}")
        else:
            print(f"  {COLORS['YELLOW']}⚠ OpenRouter API:{COLORS['RESET']} Not configured")
            print(f"  {COLORS['YELLOW']}  → Using offline fallback responses{COLORS['RESET']}")
        
        # Firebase status
        try:
            from firebase.firestore_service import firestore
            if firestore.initialized:
                print(f"  {COLORS['GREEN']}✓ Firebase:{COLORS['RESET']} Connected")
            else:
                print(f"  {COLORS['YELLOW']}⚠ Firebase:{COLORS['RESET']} Local storage mode")
        except Exception:
            print(f"  {COLORS['YELLOW']}⚠ Firebase:{COLORS['RESET']} Not configured")
        
        print(f"{COLORS['DIM']}  ─────────────────────────────────────────{COLORS['RESET']}")
        
        # Greeting message
        greeting = get_time_greeting()
        print(f"\n{COLORS['MAGENTA']}{COLORS['BOLD']}  🤖 {greeting} sir! Gwen AI is online.{COLORS['RESET']}")
        print(f"{COLORS['DIM']}  Type 'help' for commands or start chatting!{COLORS['RESET']}\n")
    
    def _start_wakeword(self):
        """Start wake word detection in background."""
        wakeword_enabled = os.getenv("WAKE_WORD_ENABLED", "true").lower() == "true"
        if wakeword_enabled:
            def on_wakeword(command: Optional[str]):
                if command:
                    print(f"\n{COLORS['CYAN']}🎤 Wake word detected! Command: {command}{COLORS['RESET']}")
                    self._process_and_respond(command)
                else:
                    print(f"\n{COLORS['CYAN']}🎤 Yes sir? I'm listening...{COLORS['RESET']}")
            
            thread = threading.Thread(
                target=wakeword.start_listening,
                args=(on_wakeword,),
                daemon=True
            )
            thread.start()
    
    # ─── MAIN LOOP ──────────────────────────────────────────────────
    
    def _main_loop(self):
        """Main interaction loop."""
        while self.running:
            try:
                # Get user input
                user_input = self._get_input()
                
                if user_input is None:
                    continue
                
                # Process exit commands
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    self._handle_exit()
                    break
                
                # Process the input
                self._process_and_respond(user_input)
                
            except KeyboardInterrupt:
                self._handle_exit()
                break
            except Exception as e:
                gwen_logger.error(f"Main loop error: {e}")
                print(f"{COLORS['RED']}⚠ Error: {e}{COLORS['RESET']}")
    
    def _get_input(self) -> Optional[str]:
        """Get user input based on current mode."""
        try:
            if self.input_mode == "voice" and voice.recognizer:
                text = voice.listen(timeout=5, phrase_time_limit=10)
                if text:
                    return text
                return None
            else:
                prompt = f"{COLORS['GREEN']}{COLORS['BOLD']}You >{COLORS['RESET']} "
                user_input = input(prompt).strip()
                
                if not user_input:
                    return None
                
                # Mode switching commands
                if user_input.lower() == "/voice":
                    self.input_mode = "voice"
                    print(f"{COLORS['CYAN']}🎤 Voice input mode activated!{COLORS['RESET']}")
                    return None
                elif user_input.lower() == "/text":
                    self.input_mode = "text"
                    print(f"{COLORS['CYAN']}⌨️ Text input mode activated!{COLORS['RESET']}")
                    return None
                
                return user_input
                
        except (EOFError, KeyboardInterrupt):
            return "exit"
        except Exception as e:
            gwen_logger.error(f"Input error: {e}")
            return None
    
    # ─── PROCESSING ─────────────────────────────────────────────────
    
    def _process_and_respond(self, user_input: str):
        """Process user input and generate response."""
        # Detect emotion from input
        emotion = emotion_engine.detect_emotion(user_input)
        
        # Auto-extract memories
        memory_type = memory.auto_extract_memory(user_input)
        if memory_type:
            gwen_logger.memory(f"Memory auto-saved: [{memory_type}]")
        
        # Save short-term memory
        memory.save_short_term(user_input, context=f"emotion: {emotion}")
        
        # Process through command engine
        result = command_engine.process_input(user_input)
        
        response = result.get("response")
        action_type = result.get("type")
        
        # Generate AI response if no direct command matched
        if action_type == "chat" and response is None:
            # Get relevant memories for context
            relevant_memories = memory.get_relevant_memories(user_input, limit=5)
            emotion_context = emotion_engine.get_emotion_context()
            
            # Build context for AI
            context = {
                "user_emotion": emotion,
                "detected_emotion_context": emotion_context,
                "relevant_memories": [m["content"] for m in relevant_memories] if relevant_memories else [],
                "user_input": user_input
            }
            
            # Get AI response
            response = ai_engine.get_response(
                user_input=user_input,
                context=context
            )
        
        if response:
            # Check if we need to show motivational message
            if emotion_engine.should_encourage() and action_type != "motivation":
                encouragement = productivity.get_motivational_message()
                response = f"{response}\n\n{COLORS['YELLOW']}💪 {encouragement}{COLORS['RESET']}"
            
            # Display response
            self._display_response(response)
            
            # Speak response if voice is enabled
            if voice.voice_enabled:
                voice.speak_async(response)
            
            # Log conversation
            try:
                from firebase.firestore_service import firestore
                firestore.log_conversation(user_input, response, emotion)
            except Exception:
                pass
    
    def _display_response(self, text: str):
        """Display AI response with typing effect."""
        ai_prefix = f"{COLORS['MAGENTA']}{COLORS['BOLD']}Gwen >{COLORS['RESET']} "
        
        # Check if response contains ASCII art (productivity report)
        if "╔══════════════════════" in text:
            print(f"\n{ai_prefix}")
            print(f"{COLORS['CYAN']}{text}{COLORS['RESET']}")
            print()
            return
        
        # Simulate typing effect for natural feel
        print(f"\n{ai_prefix}", end="", flush=True)
        
        # Split by lines but show typing effect
        for char in text:
            print(f"{COLORS['WHITE']}{char}{COLORS['RESET']}", end="", flush=True)
            time.sleep(0.01)  # Slight typing delay
        
        print("\n")
    
    def _handle_exit(self):
        """Handle system exit."""
        print(f"\n{COLORS['YELLOW']}🔄 Shutting down Gwen AI...{COLORS['RESET']}")
        
        # Stop all services
        notifications.stop()
        wakeword.stop_listening()
        
        # Save state
        memory._save_local_memory()
        productivity._save_data()
        productivity._save_stats()
        
        print(f"{COLORS['GREEN']}{COLORS['BOLD']}✅ System saved. Goodbye sir! 👋{COLORS['RESET']}\n")
        self.running = False
    
    # ─── COMMAND HANDLING ───────────────────────────────────────────
    
    def _show_help(self):
        """Show help information."""
        help_text = f"""
{COLORS['CYAN']}{COLORS['BOLD']}⚡ GWEN AI - COMMANDS ⚡{COLORS['RESET']}

{COLORS['GREEN']}💬 Conversation:{COLORS['RESET']}
  Just chat naturally! Gwen understands Tamil, English, and Tanglish.

{COLORS['GREEN']}🌐 Automation:{COLORS['RESET']}
  open [app/website]     - Open an app or website
  search [query]         - Search Google
  play [song/music]      - Play music or search YouTube
  youtube [search]       - Open YouTube
  screenshot             - Take a screenshot
  lock screen            - Lock your PC
  shutdown               - Shutdown computer
  volume up/down         - Adjust volume
  mute/unmute            - Toggle audio

{COLORS['GREEN']}🎯 Productivity:{COLORS['RESET']}
  my stats / progress    - Check your level and XP
  my quests / daily      - View daily quests
  start focus            - Start a 25-min focus session
  stop focus             - End focus session
  motivate me            - Get motivation

{COLORS['GREEN']}⏰ Reminders:{COLORS['RESET']}
  remind me to [task] in [time]  - Set a reminder
  timer for [time]               - Set a timer

{COLORS['GREEN']}🎤 Voice Modes:{COLORS['RESET']}
  /voice                 - Switch to voice input
  /text                  - Switch to text input
  Say "Hey Gwen"         - Wake word activation

{COLORS['GREEN']}📖 Other:{COLORS['RESET']}
  time / date            - Check current time/date
  help                   - Show this menu
  exit / bye             - Exit Gwen AI

{COLORS['DIM']}Tip: Gwen remembers your preferences and adapts to your mood!{COLORS['RESET']}
        """
        print(help_text)


# ─── MAIN ENTRY POINT ────────────────────────────────────────────────

def main():
    """Main entry point for Gwen AI."""
    try:
        # Create Gwen AI instance
        gwen = GwenAI()
        
        # Start the system
        gwen.start()
        
    except Exception as e:
        print(f"\n{COLORS['RED']}{COLORS['BOLD']}❌ Fatal Error: {e}{COLORS['RESET']}")
        gwen_logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()