"""
parser.py - Command parsing and intent detection for Gwen AI
"""

import re
from typing import Dict, Optional, Tuple


class CommandParser:
    """Parse user commands and detect intents."""
    
    # Intent patterns mapped to commands
    INTENT_PATTERNS = {
        "open_website": [
            r"open\s+(.+?)", r"go to\s+(.+?)", r"visit\s+(.+?)",
            r"launch\s+(.+?)", r"navigate\s+to\s+(.+?)"
        ],
        "search_google": [
            r"search\s+(?:google\s+)?(?:for\s+)?(.+)",
            r"google\s+(.+)", r"look up\s+(.+)", r"find\s+(.+)"
        ],
        "play_music": [
            r"play\s+(?:music\s+)?(.+)", r"play song\s+(.+)",
            r"play\s+(.+)", r"music\s+(.+)"
        ],
        "open_youtube": [
            r"(?:open|go to|launch)\s+youtube", r"play\s+(?:in\s+)?youtube",
            r"youtube\s+(?:search\s+)?(.+)?"
        ],
        "reminder": [
            r"remind\s+(?:me\s+)?(?:to\s+)?(.+?)(?:\s+in\s+|\s+at\s+|\s+after\s+)(.+)",
            r"set\s+(?:a\s+)?reminder\s+(?:for\s+)?(?:to\s+)?(.+?)(?:\s+in\s+|\s+at\s+|\s+after\s+)(.+)",
            r"remember\s+(?:to\s+)?(.+?)(?:\s+at\s+|\s+in\s+)(.+)"
        ],
        "set_timer": [
            r"set\s+(?:a\s+)?timer\s+(?:for\s+)?(.+)",
            r"timer\s+(?:for\s+)?(.+)"
        ],
        "lock_screen": [
            r"lock\s+(?:the\s+)?(?:screen|pc|computer|system)",
            r"lock\s+(?:my\s+)?(?:pc|computer)"
        ],
        "shutdown": [
            r"shutdown\s+(?:the\s+)?(?:pc|computer|system)",
            r"turn\s+off\s+(?:the\s+)?(?:pc|computer|system)",
            r"power\s+off"
        ],
        "volume_up": [
            r"volume\s+up", r"increase\s+volume",
            r"turn\s+up\s+(?:the\s+)?volume"
        ],
        "volume_down": [
            r"volume\s+down", r"decrease\s+volume",
            r"turn\s+down\s+(?:the\s+)?volume"
        ],
        "mute": [
            r"mute\s+(?:the\s+)?(?:volume|audio|sound|pc)?",
            r"turn\s+off\s+(?:the\s+)?(?:audio|sound)"
        ],
        "unmute": [
            r"unmute\s+(?:the\s+)?(?:volume|audio|sound|pc)?",
            r"turn\s+on\s+(?:the\s+)?(?:audio|sound)"
        ],
        "screenshot": [
            r"take\s+(?:a\s+)?screenshot", r"capture\s+(?:the\s+)?screen",
            r"screenshot"
        ],
        "create_note": [
            r"note\s+(?:down\s+)?(.+)", r"write\s+(?:a\s+)?note\s+(.+)",
            r"make\s+(?:a\s+)?note\s+(.+)", r"remember\s+(.+)"
        ],
        "weather": [
            r"weather\s+(?:in\s+|for\s+)?(.+)?",
            r"(?:what('s| is)\s+)?(?:the\s+)?(?:temperature|weather|climate)"
        ],
        "time": [
            r"(?:what('s| is)\s+)?(?:the\s+)?time",
            r"(?:current|present)\s+time"
        ],
        "date": [
            r"(?:what('s| is)\s+)?(?:the\s+)?(?:date|day|today)",
            r"today('s| is)\s+(?:date|day)"
        ],
        "productivity": [
            r"(?:show|check|view)\s+(?:my\s+)?(?:productivity|stats|progress|level|x[pP]+?)",
            r"(?:my\s+)?(?:quests|achievements|streak|rank)"
        ],
        "focus_session": [
            r"start\s+(?:a\s+)?focus\s+(?:session|mode|timer)",
            r"focus\s+(?:session|mode|timer)",
            r"study\s+(?:session|mode)"
        ],
        "stop_focus": [
            r"stop\s+(?:the\s+)?focus\s+(?:session|mode)",
            r"end\s+(?:the\s+)?focus\s+(?:session|mode)"
        ],
        "daily_quests": [
            r"(?:show|get|list|view)\s+(?:my\s+)?(?:daily\s+)?quests",
            r"(?:what('s| are)\s+)?(?:today('s| is)\s+)?(?:quests|tasks|missions)"
        ],
        "motivation": [
            r"motivate\s+me", r"(?:give|need)\s+(?:some\s+)?motivation",
            r"inspire\s+me", r"(?:make|cheer)\s+me\s+up"
        ],
        "emotional_check": [
            r"how\s+are\s+you", r"(?:how('s| is)\s+)?(?:your\s+)?day",
            r"how\s+(?:are\s+)?you\s+(?:doing|feeling)"
        ]
    }
    
    @staticmethod
    def parse_intent(text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse user input and detect intent.
        Returns (intent_type, extracted_parameter) or (None, None).
        """
        text_lower = text.lower().strip()
        
        for intent, patterns in CommandParser.INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    # Extract the main parameter (group 1 or full match)
                    param = match.group(1).strip() if match.lastindex and match.group(1) else text
                    return intent, param
        
        return None, None
    
    @staticmethod
    def is_greeting(text: str) -> bool:
        """Check if input is a greeting."""
        greetings = [
            r"\bhi\b", r"\bhello\b", r"\bhey\b", r"\bhai\b",
            r"\bgood\s*(morning|afternoon|evening|night)\b",
            r"vanakkam", r"\bepdi\s+iruk[a,i]"
        ]
        return any(re.search(g, text.lower()) for g in greetings)
    
    @staticmethod
    def is_goodbye(text: str) -> bool:
        """Check if input is a goodbye."""
        goodbyes = [
            r"\bbye\b", r"\bgoodbye\b", r"see you", r"later",
            r"po[g,k][u,r]ren", r"varen", r"\bexit\b", r"\bquit\b"
        ]
        return any(re.search(g, text.lower()) for g in goodbyes)
    
    @staticmethod
    def is_thanks(text: str) -> bool:
        """Check if input is a thank you."""
        thanks = [
            r"\bthanks?\b", r"thank you", r"thx", r"nandri",
            r"\bromba\s+nandri\b"
        ]
        return any(re.search(t, text.lower()) for t in thanks)