"""
ai_engine.py - AI engine using OpenRouter API for Gwen AI
"""

import os
import json
import time
import random
from typing import Optional, Dict, Any, List, Generator
from datetime import datetime

from utils.logger import gwen_logger
from utils.helpers import load_json, save_json, get_time_greeting


class AIEngine:
    """
    AI engine that connects to OpenRouter API for intelligent responses.
    Supports multiple free models with streaming responses.
    """
    
    # Available free models on OpenRouter
    MODELS = {
        "deepseek": "deepseek/deepseek-chat:free",
        "qwen": "qwen/qwen2.5-7b-instruct:free",
        "mistral": "mistralai/mistral-7b-instruct:free",
        "llama": "meta-llama/llama-3.2-3b-instruct:free",
        "gemini": "google/gemini-2.0-flash-exp:free"
    }
    
    def __init__(self):
        """Initialize AI engine."""
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.current_model = os.getenv("OPENROUTER_MODEL", "deepseek")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/gwen-ai",
            "X-Title": "Gwen AI Assistant"
        }
        
        # Conversation context
        self.system_prompt = self._load_system_prompt()
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 20  # Keep last 20 exchanges
        
        # Load personality prompts
        self.personality_prompt = self._load_prompt_file("personality_prompt.txt")
        self.emotion_prompt = self._load_prompt_file("emotion_prompt.txt")
        self.memory_prompt = self._load_prompt_file("memory_prompt.txt")
        
        # Fallback responses if API is unavailable
        self.fallback_responses = self._load_fallback_responses()
    
    def _load_system_prompt(self) -> str:
        """Load or create system prompt."""
        try:
            personality = self._load_prompt_file("personality_prompt.txt")
            emotion = self._load_prompt_file("emotion_prompt.txt")
            memory = self._load_prompt_file("memory_prompt.txt")
            
            return f"{personality}\n\n{emotion}\n\n{memory}"
        except Exception:
            return "You are Gwen, a futuristic female AI assistant. Be helpful, friendly, and natural."
    
    def _load_prompt_file(self, filename: str) -> str:
        """Load a prompt file from the prompts directory."""
        try:
            path = os.path.join("prompts", filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception as e:
            gwen_logger.warning(f"Failed to load prompt file {filename}: {e}")
        return ""
    
    def _load_fallback_responses(self) -> Dict[str, List[str]]:
        """Load fallback responses for when API is unavailable."""
        return {
            "greeting": [
                f"{get_time_greeting()} sir! Nalla irukeengala?",
                f"{get_time_greeting()} sir! How can I help you today?",
                f"Hey sir! {get_time_greeting()}! Enna help pannanum?"
            ],
            "general": [
                "I understand sir. Let me help you with that.",
                "Interesting sir! Let me think about that.",
                "Sure sir, I can help you with that!",
                "Naan irukken sir! Tell me what you need."
            ],
            "thanks": [
                "You're welcome sir! Always happy to help!",
                "Welcome sir! Anything else you need?",
                "Sir, it's my pleasure! Naan eppodhum ready!"
            ],
            "goodbye": [
                "Goodbye sir! Take care and come back soon!",
                "Bye sir! Have a great day ahead!",
                "Sari sir, I'll be here when you need me! Bye!"
            ],
            "confused": [
                "I'm not sure I understood that correctly sir. Could you please explain again?",
                "Sorry sir, I didn't quite catch that. Can you rephrase?",
                "Sir, konjam confusion iruku. Can you say that again?"
            ],
            "error": [
                "I'm sorry sir, I'm facing a technical issue right now. Please try again later.",
                "Sir, error varuthu. Let me restart and try again.",
                "Technical glitch sir! Just a moment please."
            ]
        }
    
    def set_model(self, model_name: str) -> bool:
        """Switch AI model."""
        if model_name in self.MODELS:
            self.current_model = model_name
            gwen_logger.system(f"Switched to model: {model_name}")
            return True
        gwen_logger.warning(f"Unknown model: {model_name}")
        return False
    
    def set_api_key(self, api_key: str):
        """Set OpenRouter API key."""
        self.api_key = api_key
        self.headers["Authorization"] = f"Bearer {api_key}"
        gwen_logger.system("API key updated")
    
    def add_context(self, context: Dict[str, Any]):
        """Add context (memories, emotions) to system prompt."""
        context_str = "\n\nCONTEXT:\n"
        for key, value in context.items():
            if value:
                context_str += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
        
        if context_str != "\n\nCONTEXT:\n":
            self.system_prompt = self._load_system_prompt() + context_str
    
    def get_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get AI response for user input.
        
        Args:
            user_input: User's message
            context: Optional context (memories, emotions, etc.)
        
        Returns:
            AI response text
        """
        # Add context if provided
        if context:
            self.add_context(context)
        
        # Try API first
        try:
            response = self._call_openrouter(user_input)
            if response:
                # Save to conversation history
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": response})
                self._trim_history()
                
                return response
        except Exception as e:
            gwen_logger.error(f"OpenRouter API call failed: {e}")
        
        # Fallback response
        return self._get_fallback_response(user_input)
    
    def get_response_stream(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Get streaming AI response.
        
        Args:
            user_input: User's message
            context: Optional context
        
        Yields:
            Response chunks
        """
        if context:
            self.add_context(context)
        
        try:
            yield from self._call_openrouter_stream(user_input)
        except Exception as e:
            gwen_logger.error(f"Stream failed: {e}")
            yield self._get_fallback_response(user_input)
    
    def _call_openrouter(self, user_input: str) -> Optional[str]:
        """Call OpenRouter API for response."""
        if not self.api_key:
            gwen_logger.warning("OpenRouter API key not set")
            return None
        
        try:
            import httpx
            
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history
            messages.extend(self.conversation_history[-10:])  # Last 10 exchanges
            messages.append({"role": "user", "content": user_input})
            
            payload = {
                "model": self.MODELS.get(self.current_model),
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    gwen_logger.error(f"API error {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            gwen_logger.error(f"OpenRouter request failed: {e}")
            return None
    
    def _call_openrouter_stream(self, user_input: str) -> Generator[str, None, None]:
        """Call OpenRouter API with streaming response."""
        if not self.api_key:
            yield self._get_fallback_response(user_input)
            return
        
        try:
            import httpx
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history[-10:],
                {"role": "user", "content": user_input}
            ]
            
            payload = {
                "model": self.MODELS.get(self.current_model),
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": True
            }
            
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", self.base_url, headers=self.headers, json=payload) as response:
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            if line.startswith("data: "):
                                data = line[6:]
                                if data != "[DONE]":
                                    try:
                                        chunk = json.loads(data)
                                        content = chunk["choices"][0]["delta"].get("content", "")
                                        if content:
                                            full_response += content
                                            yield content
                                    except (json.JSONDecodeError, KeyError):
                                        pass
            
            # Save to history after full response
            if full_response:
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": full_response})
                self._trim_history()
                
        except Exception as e:
            gwen_logger.error(f"OpenRouter stream failed: {e}")
            yield self._get_fallback_response(user_input)
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Get a fallback response when API is unavailable."""
        text_lower = user_input.lower()
        
        # Check for known patterns
        if any(g in text_lower for g in ["hi", "hello", "hey", "vanakkam", "epdi"]):
            return random.choice(self.fallback_responses["greeting"])
        elif any(b in text_lower for b in ["bye", "goodbye", "exit", "quit"]):
            return random.choice(self.fallback_responses["goodbye"])
        elif any(t in text_lower for t in ["thanks", "thank you", "thx"]):
            return random.choice(self.fallback_responses["thanks"])
        elif any(c in text_lower for c in ["how are you", "how do you", "what's up"]):
            return f"I'm doing great sir! Ready to help you. How about you?"
        else:
            return random.choice(self.fallback_responses["general"])
    
    def _trim_history(self):
        """Trim conversation history to max length."""
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        gwen_logger.ai("Conversation history cleared")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of recent conversation topics."""
        if not self.conversation_history:
            return "No recent conversations."
        
        topics = set()
        for msg in self.conversation_history[-10:]:
            if msg["role"] == "user":
                # Extract key words as topics
                words = msg["content"].lower().split()[:5]
                topics.update(words)
        
        return f"Recent topics: {', '.join(list(topics)[:10])}"


# Global AI engine instance
ai_engine = AIEngine()