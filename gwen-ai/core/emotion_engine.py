"""
emotion_engine.py - Emotional intelligence engine for Gwen AI
"""

import re
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import deque

from utils.logger import gwen_logger
from utils.helpers import load_json, save_json


class EmotionEngine:
    """
    Emotional AI that detects user emotions from text patterns,
    interaction frequency, and conversation style.
    """
    
    EMOTIONS = [
        "neutral", "happy", "sad", "stressed", "excited", 
        "motivated", "anxious", "angry", "tired", "grateful",
        "curious", "confused", "bored", "burnout"
    ]
    
    # Emotion detection patterns
    EMOTION_PATTERNS = {
        "stressed": [
            r"\bstress\w*\b", r"\boverwhelm\w*\b", r"\btoo much\b",
            r"\bcan'?t handle\b", r"\bexhaust\w*\b", r"\bburn(ed)? out\b",
            r"\btoo many\b", r"\bpressure\b", r"\bdepress\w*\b"
        ],
        "sad": [
            r"\bsad\b", r"\bunhappy\b", r"\blonely\b", r"\bbroken\b",
            r"\bdepress\w*\b", r"\bcry\w*\b", r"\bhurt\b", r"\bdown\b",
            r"\blow\b", r"\bsorry\b"
        ],
        "excited": [
            r"\bexcit\w*\b", r"\bamazing\b", r"\bincredible\b", r"\bwow\b",
            r"\bhooray\b", r"\byay\b", r"\b🎉\b", r"\bawesome\b",
            r"\bfantastic\b", r"\bgreat\b"
        ],
        "motivated": [
            r"\bmotivat\w*\b", r"\bready\b", r"\bfocus\b", r"\bgrind\b",
            r"\bwork hard\b", r"\bstudy\b", r"\bgoal\b", r"\bachieve\b",
            r"\bproductivity\b", r"\blevel up\b"
        ],
        "anxious": [
            r"\banxi\w*\b", r"\bworr\w*\b", r"\bnervous\b", r"\bscared\b",
            r"\bpanic\b", r"\bafraid\b", r"\bfear\b", r"\buncertain\b",
            r"\bwhat if\b"
        ],
        "angry": [
            r"\bangr\w*\b", r"\bfrustrat\w*\b", r"\bannoy\w*\b", r"\brage\b",
            r"\bpiss\w*\b", r"\bfurious\b", r"\bdamn\b", r"\bhate\b",
            r"\bstupid\b", r"\bsuck\w*\b"
        ],
        "tired": [
            r"\btired\b", r"\bsleepy\b", r"\bexhaust\w*\b", r"\bdrain\w*\b",
            r"\bno energy\b", r"\bfatigue\b", r"\bweak\b", r"\bworn out\b"
        ],
        "grateful": [
            r"\bthank\w*\b", r"\bgrateful\b", r"\bblessed\b", r"\bappreciate\b",
            r"\bgrateful\b", r"\bthankful\b"
        ],
        "curious": [
            r"\bcurious\b", r"\bwonder\b", r"\bhow\b", r"\bwhy\b",
            r"\bwhat\b", r"\btell me\b", r"\bexplain\b"
        ],
        "confused": [
            r"\bconfus\w*\b", r"\bdon'?t understand\b", r"\bunclear\b",
            r"\bwhat do you mean\b", r"\bhuh\b"
        ],
        "burnout": [
            r"\bburnout\b", r"\bbreak down\b", r"\bcannot continue\b",
            r"\bgive up\b", r"\bquit\b", r"\bno motivation\b",
            r"\bdon'?t want to\b", r"\bcan'?t do this\b"
        ]
    }
    
    def __init__(self):
        """Initialize emotion engine."""
        self.current_emotion = "neutral"
        self.emotion_history: List[Dict[str, Any]] = []
        self.emotion_scores: Dict[str, float] = {e: 0.0 for e in self.EMOTIONS}
        self.max_history = 100
        
        # Interaction tracking for emotion detection
        self.interaction_times: deque = deque(maxlen=20)
        self.typing_speed_history: deque = deque(maxlen=10)
        self.message_lengths: deque = deque(maxlen=20)
        
        # Emotional state persistence
        self.emotion_state_path = "data/emotion_state.json"
        self._load_state()
        
        gwen_logger.system("Emotion engine initialized")
    
    def _load_state(self):
        """Load emotional state from disk."""
        state = load_json(self.emotion_state_path)
        if state:
            self.emotion_history = state.get("history", [])
            self.current_emotion = state.get("current", "neutral")
    
    def _save_state(self):
        """Save emotional state to disk."""
        save_json(self.emotion_state_path, {
            "history": self.emotion_history[-50:],
            "current": self.current_emotion
        })
    
    # ─── EMOTION DETECTION ──────────────────────────────────────────
    
    def detect_emotion(self, text: str) -> str:
        """
        Detect user's emotional state from text.
        
        Args:
            text: User's input text
        
        Returns:
            Detected emotion string
        """
        text_lower = text.lower()
        scores = {emotion: 0 for emotion in self.EMOTIONS}
        
        # Score based on keyword patterns
        for emotion, patterns in self.EMOTION_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                scores[emotion] += len(matches) * 2
        
        # Text signals
        word_count = len(text_lower.split())
        self.message_lengths.append(word_count)
        
        # Very short messages might indicate low energy
        if word_count <= 2:
            scores["tired"] += 0.5
        
        # Long messages with emotional content
        if word_count > 20 and scores["stressed"] > 0:
            scores["stressed"] += 2
        
        # Exclamation marks indicate strong emotions
        exclamation_count = text.count("!")
        if exclamation_count > 0:
            if scores["angry"] > scores["excited"]:
                scores["angry"] += exclamation_count
            else:
                scores["excited"] += exclamation_count
        
        # Question marks with emotion words
        question_count = text.count("?")
        if question_count > 0 and scores["anxious"] > 0:
            scores["anxious"] += question_count * 0.5
        
        # Caps lock indicates strong emotion
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3 and len(text) > 10:
            if scores["angry"] > scores["excited"]:
                scores["angry"] += 2
            else:
                scores["excited"] += 2
        
        # Time-based patterns
        self.interaction_times.append(datetime.now())
        recent_interactions = len(self.interaction_times)
        
        # Frequent interactions might indicate anxiety or excitement
        if recent_interactions > 10 and len(self.interaction_times) > 1:
            time_span = (self.interaction_times[-1] - self.interaction_times[0]).seconds
            if time_span < 300:  # Within 5 minutes
                if scores["stressed"] > 0:
                    scores["anxious"] += 1
        
        # Get the highest scoring emotion
        max_score = max(scores.values())
        if max_score > 0:
            detected_emotion = max(scores, key=scores.get)
        else:
            detected_emotion = "neutral"
        
        # Record emotion
        self._record_emotion(detected_emotion, max_score)
        
        return detected_emotion
    
    def _record_emotion(self, emotion: str, intensity: float):
        """Record detected emotion."""
        self.current_emotion = emotion
        self.emotion_scores[emotion] = intensity
        
        entry = {
            "emotion": emotion,
            "intensity": round(intensity, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.emotion_history.append(entry)
        
        # Trim history
        if len(self.emotion_history) > self.max_history:
            self.emotion_history = self.emotion_history[-self.max_history:]
        
        self._save_state()
        gwen_logger.system(f"Emotion detected: {emotion} ({intensity:.1f})")
    
    # ─── EMOTION ANALYSIS ───────────────────────────────────────────
    
    def get_emotional_state(self) -> Dict[str, Any]:
        """Get current comprehensive emotional state."""
        recent = self.emotion_history[-10:] if self.emotion_history else []
        
        # Calculate emotional trends
        trend = self._calculate_trend()
        
        # Determine overall mood
        if recent:
            dominant_emotions = {}
            for entry in recent:
                e = entry["emotion"]
                dominant_emotions[e] = dominant_emotions.get(e, 0) + entry["intensity"]
            
            overall_mood = max(dominant_emotions, key=dominant_emotions.get) if dominant_emotions else "neutral"
        else:
            overall_mood = "neutral"
        
        return {
            "current": self.current_emotion,
            "intensity": self.emotion_scores.get(self.current_emotion, 0),
            "overall_mood": overall_mood,
            "trend": trend,
            "recent_emotions": [e["emotion"] for e in recent[-5:]],
            "stability": self._calculate_stability()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate emotional trend (improving, declining, stable)."""
        if len(self.emotion_history) < 5:
            return "stable"
        
        recent = self.emotion_history[-5:]
        positive_emotions = {"happy", "excited", "motivated", "grateful", "curious"}
        negative_emotions = {"sad", "stressed", "angry", "tired", "anxious", "burnout"}
        
        positive_count = sum(1 for e in recent if e["emotion"] in positive_emotions)
        negative_count = sum(1 for e in recent if e["emotion"] in negative_emotions)
        
        if positive_count > negative_count + 1:
            return "improving"
        elif negative_count > positive_count + 1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_stability(self) -> float:
        """Calculate emotional stability (0-1)."""
        if len(self.emotion_history) < 5:
            return 1.0
        
        recent = self.emotion_history[-5:]
        unique_emotions = len(set(e["emotion"] for e in recent))
        
        # More unique emotions = less stable
        return max(0, 1 - (unique_emotions / len(self.EMOTIONS)))
    
    def should_encourage(self) -> bool:
        """Check if user needs encouragement based on emotional state."""
        negative_emotions = {"sad", "stressed", "tired", "anxious", "burnout", "confused"}
        
        if self.current_emotion in negative_emotions:
            # Check if this is a pattern
            recent = self.emotion_history[-10:] if self.emotion_history else []
            negative_count = sum(1 for e in recent if e["emotion"] in negative_emotions)
            
            # Encourage if more than half recent emotions are negative
            if len(recent) > 0 and negative_count / len(recent) > 0.5:
                return True
        
        return False
    
    def get_emotion_context(self) -> Dict[str, Any]:
        """Get emotional context for AI system prompt."""
        state = self.get_emotional_state()
        
        context = {
            "user_emotion": state["current"],
            "mood_trend": state["trend"],
            "emotional_stability": state["stability"],
            "needs_encouragement": self.should_encourage()
        }
        
        return context
    
    def get_emotion_response_suggestion(self) -> Optional[str]:
        """
        Get a suggested response style based on detected emotion.
        Returns None if no special response needed.
        """
        suggestions = {
            "stressed": "Be calm and reassuring. Suggest breaks and relaxation.",
            "sad": "Be gentle and caring. Offer support and motivation.",
            "excited": "Match their energy. Celebrate with them.",
            "motivated": "Reinforce their drive. Help them stay focused.",
            "anxious": "Be reassuring and confident. Break things down.",
            "angry": "Stay calm. Don't match anger. Offer solutions.",
            "tired": "Be understanding. Suggest rest or light activities.",
            "burnout": "Encourage breaks. Remind of past achievements.",
            "confused": "Be patient. Explain clearly and simply.",
            "curious": "Be informative and engaging. Encourage exploration."
        }
        
        return suggestions.get(self.current_emotion)
    
    def reset_emotion_state(self):
        """Reset emotional state to neutral."""
        self.current_emotion = "neutral"
        self.emotion_scores = {e: 0.0 for e in self.EMOTIONS}
        self.emotion_history = []
        self._save_state()
        gwen_logger.system("Emotion state reset")


# Global emotion engine instance
emotion_engine = EmotionEngine()