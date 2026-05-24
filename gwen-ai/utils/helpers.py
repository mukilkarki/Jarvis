"""
helpers.py - Utility helper functions for Gwen AI
"""

import os
import json
import re
import time
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional


def load_json(filepath: str) -> dict:
    """Load JSON file safely."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[Helper] Error loading {filepath}: {e}")
    return {}


def save_json(filepath: str, data: dict) -> bool:
    """Save data to JSON file safely."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, TypeError) as e:
        print(f"[Helper] Error saving {filepath}: {e}")
        return False


def generate_id(prefix: str = "gw") -> str:
    """Generate unique ID."""
    timestamp = int(time.time() * 1000)
    hash_input = f"{prefix}{timestamp}{os.urandom(4).hex()}"
    return f"{prefix}_{hashlib.md5(hash_input.encode()).hexdigest()[:12]}"


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s.,!?\-:;\'\"@#$%&()]', '', text)
    return text


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract basic entities from text."""
    entities = {
        "time": [],
        "date": [],
        "numbers": [],
        "urls": []
    }
    
    # Extract URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
    entities["urls"] = re.findall(url_pattern, text)
    
    # Extract numbers
    num_pattern = r'\b\d+\b'
    entities["numbers"] = re.findall(num_pattern, text)
    
    # Extract time patterns
    time_pattern = r'\b(?:[01]?\d|2[0-3]):[0-5]\d\b'
    entities["time"] = re.findall(time_pattern, text)
    
    return entities


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format timestamp for display."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def calculate_importance(text: str) -> int:
    """Calculate memory importance score (1-10)."""
    score = 5  # Base score
    
    # Keywords that indicate importance
    high_importance = ["remember", "important", "never forget", "always", 
                      "favorite", "love", "hate", "best", "worst", "goal",
                      "dream", "birthday", "anniversary", "fear", "passion"]
    
    medium_importance = ["like", "want", "need", "must", "should", "usually",
                        "often", "sometimes", "habit", "routine", "plan"]
    
    text_lower = text.lower()
    
    for word in high_importance:
        if word in text_lower:
            score += 2
    
    for word in medium_importance:
        if word in text_lower:
            score += 1
    
    # Length bonus
    if len(text) > 100:
        score += 1
    if len(text) > 200:
        score += 1
    
    return min(10, max(1, score))


def detect_language(text: str) -> str:
    """Detect if text is Tamil, English, or Tanglish."""
    tamil_chars = re.findall(r'[\u0B80-\u0BFF]', text)
    if len(tamil_chars) > 3:
        return "tamil"
    
    tanglish_patterns = [
        r'\b(?:epdi|enga|enna|yaen|poda|podi|da|di|mapla|thala|saamy)\b',
        r'\b(?:sir|naan|nee|avan|aval|ivar|athu|ithu)\b',
        r'[a-z]+unga\b',
        r'[a-z]+ing\b'
    ]
    
    for pattern in tanglish_patterns:
        if re.search(pattern, text.lower()):
            return "tanglish"
    
    return "english"


def get_time_greeting() -> str:
    """Get time-appropriate greeting."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


def sanitize_firebase_doc_id(text: str) -> str:
    """Sanitize text for use as Firebase document ID."""
    # Firebase doc IDs cannot contain . / [ ] or match __.*__
    sanitized = re.sub(r'[\./\[\]]', '_', text)
    sanitized = re.sub(r'^__|__$', '', sanitized)
    return sanitized[:100]