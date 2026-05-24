"""
command_engine.py - Command processing and routing engine for Gwen AI
"""

import os
import sys
import random
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Callable

from utils.logger import gwen_logger
from utils.parser import CommandParser
from utils.helpers import detect_language, get_time_greeting
from core.automation_engine import automation
from core.emotion_engine import emotion_engine
from core.memory_engine import memory
from core.productivity_engine import productivity
from core.notification_engine import notifications


class CommandEngine:
    """
    Command processing engine that routes user input to appropriate handlers.
    Handles automation, productivity, memory, and AI chat routing.
    """
    
    def __init__(self):
        """Initialize command engine."""
        self.parser = CommandParser()
        gwen_logger.system("Command engine initialized")
    
    def process_input(self, text: str) -> Dict[str, Any]:
        """
        Process user input and determine action.
        
        Args:
            text: User's input text
        
        Returns:
            Dict with action type and response
        """
        if not text or not text.strip():
            return {"type": "none", "response": "Yes sir?"}
        
        text = text.strip()
        
        # Check for greetings
        if self.parser.is_greeting(text):
            return self._handle_greeting(text)
        
        # Check for goodbyes
        if self.parser.is_goodbye(text):
            return self._handle_goodbye(text)
        
        # Check for thanks
        if self.parser.is_thanks(text):
            return self._handle_thanks()
        
        # Parse intent
        intent, param = self.parser.parse_intent(text)
        
        if intent:
            handler = self._get_handler(intent)
            if handler:
                return handler(text, intent, param)
        
        # No specific intent found - route to AI chat
        return {"type": "chat", "response": None, "input": text}
    
    def _get_handler(self, intent: str) -> Optional[Callable]:
        """Get the handler function for an intent."""
        handlers = {
            "open_website": self._handle_open_website,
            "search_google": self._handle_search,
            "play_music": self._handle_play_music,
            "open_youtube": self._handle_open_youtube,
            "reminder": self._handle_reminder,
            "set_timer": self._handle_set_timer,
            "lock_screen": self._handle_lock_screen,
            "shutdown": self._handle_shutdown,
            "screenshot": self._handle_screenshot,
            "volume_up": self._handle_volume_up,
            "volume_down": self._handle_volume_down,
            "mute": self._handle_mute,
            "unmute": self._handle_unmute,
            "time": self._handle_time,
            "date": self._handle_date,
            "productivity": self._handle_productivity,
            "daily_quests": self._handle_daily_quests,
            "focus_session": self._handle_focus_session,
            "stop_focus": self._handle_stop_focus,
            "motivation": self._handle_motivation,
            "emotional_check": self._handle_emotional_check
        }
        return handlers.get(intent)
    
    # ─── HANDLER METHODS ────────────────────────────────────────────
    
    def _handle_greeting(self, text: str) -> Dict[str, Any]:
        """Handle greeting."""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        responses = [
            f"{greeting} sir! Nalla irukeengala?",
            f"{greeting} sir! How can I assist you today?",
            f"{greeting} sir! Enna help pannanum?",
            f"Hey sir! {greeting}! Ready for another productive day?"
        ]
        
        return {"type": "greeting", "response": random.choice(responses)}
    
    def _handle_goodbye(self, text: str) -> Dict[str, Any]:
        """Handle goodbye."""
        responses = [
            "Goodbye sir! Take care! I'll be here when you need me.",
            "Bye sir! Have a great day! Naan irukken!",
            "Sari sir! Talk to you later! Stay awesome!",
            "Goodbye sir! Don't forget to check your quests tomorrow!"
        ]
        return {"type": "goodbye", "response": random.choice(responses)}
    
    def _handle_thanks(self) -> Dict[str, Any]:
        """Handle thanks."""
        responses = [
            "You're welcome sir! Always happy to help!",
            "Welcome sir! Naan eppodhum ready!",
            "My pleasure sir! Anything else you need?",
            "Sir, it's my duty! Happy to assist!"
        ]
        return {"type": "thanks", "response": random.choice(responses)}
    
    def _handle_open_website(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle opening a website."""
        if not param:
            return {"type": "error", "response": "Which website should I open sir?"}
        
        success, message = automation.open_website(param)
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_search(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle Google search."""
        if not param:
            return {"type": "error", "response": "What should I search for sir?"}
        
        success, message = automation.search_google(param)
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_play_music(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle playing music."""
        if param and param not in ["music", "song"]:
            # Search for the song on YouTube
            success, message = automation.open_youtube(param)
            return {"type": "automation", "response": message, "success": success}
        else:
            # Try opening Spotify or default music player
            success, message = automation.open_app("spotify")
            if not success:
                message = "I don't have a music app configured sir. Would you like me to play something on YouTube?"
            return {"type": "automation", "response": message, "success": success}
    
    def _handle_open_youtube(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle opening YouTube."""
        success, message = automation.open_youtube(param if param else None)
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_reminder(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle setting a reminder."""
        # Parse reminder: "remind me to [task] in [time]"
        import re
        match = re.search(r"remind\s+(?:me\s+)?(?:to\s+)?(.+?)(?:\s+in\s+|\s+after\s+)(\d+)\s*(minute|hour|min|hr)s?", text.lower())
        
        if match:
            task = match.group(1).strip()
            amount = int(match.group(2))
            unit = match.group(3)
            
            delay = amount * 60 if unit in ["hour", "hr"] else amount
            
            success = notifications.set_reminder(task, delay)
            if success:
                time_str = f"{amount} {unit}" if amount > 1 else f"{amount} {unit}"
                return {"type": "reminder", "response": f"Sure sir! I'll remind you to {task} in {time_str}."}
            else:
                return {"type": "error", "response": "Sorry sir, I couldn't set that reminder."}
        
        # If we couldn't parse the time, just save as a general reminder
        if param:
            memory.save_memory(f"Reminder: {param}", "reminders", importance=8)
            return {"type": "reminder", "response": f"I'll remember that sir! I'll remind you about {param}."}
        
        return {"type": "error", "response": "What should I remind you about sir?"}
    
    def _handle_set_timer(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle setting a timer."""
        import re
        match = re.search(r"(\d+)\s*(minute|min|second|sec|hour|hr)s?", param.lower() if param else "")
        
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit in ["hour", "hr"]:
                delay = amount * 60
                time_str = f"{amount} hour{'s' if amount > 1 else ''}"
            elif unit in ["second", "sec"]:
                delay = amount / 60
                time_str = f"{amount} second{'s' if amount > 1 else ''}"
            else:
                delay = amount
                time_str = f"{amount} minute{'s' if amount > 1 else ''}"
            
            if delay < 1:
                delay = 1
            
            success = notifications.set_reminder("timer", int(delay))
            if success:
                return {"type": "timer", "response": f"Timer set for {time_str} sir! I'll notify you."}
        
        return {"type": "error", "response": "For how long should I set the timer sir?"}
    
    def _handle_lock_screen(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle lock screen."""
        success, message = automation.lock_screen()
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_shutdown(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle shutdown."""
        success, message = automation.shutdown()
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_screenshot(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle screenshot."""
        path = automation.take_screenshot()
        if path:
            return {"type": "automation", "response": f"Screenshot saved sir! Check it out at {path}"}
        return {"type": "error", "response": "Sorry sir, couldn't take screenshot."}
    
    def _handle_volume_up(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle volume up."""
        success, message = automation.volume_up()
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_volume_down(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle volume down."""
        success, message = automation.volume_down()
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_mute(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle mute."""
        success, message = automation.mute()
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_unmute(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle unmute."""
        success, message = automation.unmute()
        return {"type": "automation", "response": message, "success": success}
    
    def _handle_time(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle time query."""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        return {"type": "info", "response": f"Sir, it's {time_str} now."}
    
    def _handle_date(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle date query."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return {"type": "info", "response": f"Sir, today is {date_str}."}
    
    def _handle_productivity(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle productivity stats query."""
        stats = productivity.get_stats()
        report = productivity.get_progress_report()
        message = productivity.get_motivational_message()
        
        return {
            "type": "productivity",
            "response": f"{message}\n{report}",
            "data": stats
        }
    
    def _handle_daily_quests(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle daily quests display."""
        quests = productivity.get_daily_quests()
        
        if not quests:
            return {"type": "productivity", "response": "No quests available today sir."}
        
        response = "📋 Today's Quests:\n\n"
        for i, quest in enumerate(quests, 1):
            status = "✅" if quest["completed"] else "⬜"
            response += f"{status} {i}. {quest['name']} - {quest['description']} (+{quest['xp']} XP)\n"
        
        response += f"\nType 'complete quest [number]' to mark a quest as done!"
        
        return {"type": "productivity", "response": response, "data": quests}
    
    def _handle_focus_session(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle focus session start."""
        session = productivity.start_focus_session()
        return {
            "type": "focus",
            "response": "🎯 Focus session started sir! I'll keep you focused for 25 minutes. Let me know if you need anything!",
            "data": session
        }
    
    def _handle_stop_focus(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle focus session stop."""
        sessions = productivity.data.get("focus_sessions", [])
        active_sessions = [s for s in sessions if s.get("active")]
        
        if active_sessions:
            for session in active_sessions:
                xp = productivity.complete_focus_session(session["id"])
                return {
                    "type": "focus",
                    "response": f"Great focus session sir! You earned {xp} XP! Keep the momentum going! 🎯"
                }
        
        return {"type": "focus", "response": "No active focus session sir. Would you like to start one?"}
    
    def _handle_motivation(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle motivation request."""
        message = productivity.get_motivational_message()
        
        extra_messages = [
            "Remember sir, every small step counts towards your goal!",
            "You have the power to achieve anything you set your mind to!",
            "The journey of a thousand miles begins with a single step!",
            "You're stronger than you think, sir! Keep pushing forward!",
            "Great things never come from comfort zones! Stay focused!"
        ]
        
        return {
            "type": "motivation",
            "response": f"{message}\n\n{random.choice(extra_messages)}"
        }
    
    def _handle_emotional_check(self, text: str, intent: str, param: Optional[str]) -> Dict[str, Any]:
        """Handle emotional check-in."""
        emotion = emotion_engine.get_emotional_state()
        
        responses = [
            f"I'm doing great sir! Ready to help you level up! How are you feeling today?",
            f"I'm always good when I'm with you sir! Tell me about your day!",
            f"Operating at 100% sir! More importantly, how are you doing?"
        ]
        
        return {
            "type": "chat",
            "response": random.choice(responses),
            "emotion": emotion
        }


# Global command engine instance
command_engine = CommandEngine()