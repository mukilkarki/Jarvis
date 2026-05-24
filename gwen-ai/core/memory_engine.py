"""
memory_engine.py - Long-term memory system for Gwen AI
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from utils.logger import gwen_logger
from utils.helpers import load_json, save_json, calculate_importance, generate_id
from firebase.firestore_service import firestore


class MemoryEngine:
    """
    Long-term memory system that remembers user information, 
    habits, goals, emotions, and preferences.
    """
    
    MEMORY_TYPES = [
        "short_term", "long_term", "emotional", 
        "habits", "goals", "reminders", "preferences"
    ]
    
    def __init__(self):
        """Initialize memory engine."""
        self.local_memory_path = "data/local_memory.json"
        self.local_memory = self._load_local_memory()
        self.short_term: List[Dict[str, Any]] = []
        self.max_short_term = 20
        
        gwen_logger.memory("Memory engine initialized")
    
    def _load_local_memory(self) -> Dict[str, Any]:
        """Load local memory cache."""
        return load_json(self.local_memory_path)
    
    def _save_local_memory(self):
        """Save local memory cache."""
        save_json(self.local_memory_path, self.local_memory)
    
    # ─── MEMORY CREATION ────────────────────────────────────────────
    
    def save_memory(self, content: str, memory_type: str = "long_term", 
                   importance: Optional[int] = None, category: str = "general",
                   context: str = "") -> bool:
        """
        Save a new memory.
        
        Args:
            content: Memory content
            memory_type: Type of memory (long_term, habit, goal, etc.)
            importance: Importance score (1-10). Auto-calculated if None.
            category: Memory category
            context: Context of when this was saved
        """
        if content.strip() == "":
            return False
        
        if memory_type not in self.MEMORY_TYPES:
            memory_type = "long_term"
        
        if importance is None:
            importance = calculate_importance(content)
        
        memory = {
            "id": generate_id("mem"),
            "type": memory_type,
            "content": content.strip(),
            "importance": importance,
            "category": category,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": datetime.now().isoformat()
        }
        
        # Save to local cache
        mem_id = memory["id"]
        if "memories" not in self.local_memory:
            self.local_memory["memories"] = {}
        self.local_memory["memories"][mem_id] = memory
        self._save_local_memory()
        
        # Save to Firestore
        firestore.save_memory(memory)
        
        gwen_logger.memory(f"Memory saved [{memory_type}] (importance: {importance}): {content[:50]}...")
        return True
    
    def save_short_term(self, content: str, context: str = ""):
        """Save a short-term memory (conversation context)."""
        memory = {
            "id": generate_id("stm"),
            "content": content,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        self.short_term.append(memory)
        
        # Trim short-term memory
        if len(self.short_term) > self.max_short_term:
            self.short_term = self.short_term[-self.max_short_term:]
        
        # Auto-promote important short-term to long-term
        if calculate_importance(content) >= 7:
            self.save_memory(content, "long_term", 
                           importance=calculate_importance(content),
                           context=context)
    
    # ─── MEMORY RETRIEVAL ───────────────────────────────────────────
    
    def get_relevant_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories relevant to the current query."""
        relevant = []
        query_lower = query.lower()
        
        # Search local memories
        memories = self.local_memory.get("memories", {})
        for mem_id, memory in memories.items():
            score = self._calculate_relevance(query_lower, memory)
            if score > 0:
                relevant.append((score, memory))
        
        # Search short-term
        for stm in self.short_term:
            score = self._calculate_relevance(query_lower, {"content": stm["content"]})
            if score > 0.3:  # Lower threshold for short-term
                relevant.append((score * 0.8, stm))
        
        # Sort by relevance
        relevant.sort(key=lambda x: x[0], reverse=True)
        
        # Update access count for retrieved memories
        result = []
        for score, memory in relevant[:limit]:
            if "id" in memory and memory["id"] in memories:
                memories[memory["id"]]["access_count"] += 1
                memories[memory["id"]]["last_accessed"] = datetime.now().isoformat()
            result.append(memory)
        
        self._save_local_memory()
        
        return result
    
    def _calculate_relevance(self, query: str, memory: Dict[str, Any]) -> float:
        """Calculate relevance score between query and memory."""
        score = 0.0
        content = memory.get("content", "").lower()
        
        # Keyword matching
        query_words = set(query.split())
        content_words = set(content.split())
        common_words = query_words & content_words
        
        if common_words:
            score += len(common_words) * 0.2
        
        # Exact phrase matching
        if query in content:
            score += 0.5
        
        # Importance bonus
        importance = memory.get("importance", 5)
        score += importance * 0.05
        
        # Recency bonus (memories accessed within last 24h)
        last_accessed = memory.get("last_accessed", "")
        if last_accessed:
            try:
                last_time = datetime.fromisoformat(last_accessed)
                if datetime.now() - last_time < timedelta(hours=24):
                    score += 0.2
            except ValueError:
                pass
        
        return score
    
    def get_memories_by_type(self, memory_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get memories filtered by type."""
        if memory_type not in self.MEMORY_TYPES:
            return []
        
        memories = self.local_memory.get("memories", {})
        filtered = [
            m for m in memories.values() 
            if m.get("type") == memory_type
        ]
        filtered.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return filtered[:limit]
    
    def search_memories(self, search_term: str) -> List[Dict[str, Any]]:
        """Search memories by content."""
        memories = self.local_memory.get("memories", {})
        search_lower = search_term.lower()
        
        results = [
            m for m in memories.values()
            if search_lower in m.get("content", "").lower()
        ]
        results.sort(key=lambda x: x.get("importance", 0), reverse=True)
        return results[:20]
    
    # ─── MEMORY MANAGEMENT ──────────────────────────────────────────
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        memories = self.local_memory.get("memories", {})
        if memory_id in memories:
            del memories[memory_id]
            self._save_local_memory()
            firestore.delete_memory(memory_id)
            gwen_logger.memory(f"Memory deleted: {memory_id}")
            return True
        return False
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory."""
        memories = self.local_memory.get("memories", {})
        if memory_id in memories:
            memories[memory_id].update(updates)
            memories[memory_id]["updated_at"] = datetime.now().isoformat()
            self._save_local_memory()
            firestore.save_memory(memories[memory_id])
            gwen_logger.memory(f"Memory updated: {memory_id}")
            return True
        return False
    
    def get_all_memories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all memories grouped by type."""
        memories = self.local_memory.get("memories", {})
        grouped = {mt: [] for mt in self.MEMORY_TYPES}
        
        for mem in memories.values():
            mtype = mem.get("type", "long_term")
            if mtype in grouped:
                grouped[mtype].append(mem)
        
        return grouped
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        memories = self.local_memory.get("memories", {})
        
        if not memories:
            return {"total": 0, "types": {}, "avg_importance": 0}
        
        type_counts = {}
        total_importance = 0
        
        for mem in memories.values():
            mtype = mem.get("type", "unknown")
            type_counts[mtype] = type_counts.get(mtype, 0) + 1
            total_importance += mem.get("importance", 5)
        
        return {
            "total": len(memories),
            "types": type_counts,
            "avg_importance": round(total_importance / len(memories), 1)
        }
    
    def get_conversation_context(self) -> str:
        """Build a context string from relevant memories for AI."""
        memories = self.local_memory.get("memories", {})
        
        if not memories:
            return ""
        
        # Get most important and recent memories
        sorted_mems = sorted(
            memories.values(),
            key=lambda x: (x.get("importance", 0), x.get("access_count", 0)),
            reverse=True
        )[:15]
        
        context_parts = ["User Information and Context:"]
        for mem in sorted_mems:
            context_parts.append(f"- [{mem.get('type', 'info')}] {mem.get('content', '')}")
        
        return "\n".join(context_parts)
    
    def auto_extract_memory(self, text: str) -> Optional[str]:
        """Auto-detect if text contains important information to remember."""
        importance = calculate_importance(text)
        
        if importance >= 7:
            # Auto-save important information
            memory_type = self._detect_memory_type(text)
            self.save_memory(text, memory_type, importance)
            return memory_type
        
        return None
    
    def _detect_memory_type(self, text: str) -> str:
        """Detect the type of memory from text content."""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["goal", "want to", "plan to", "will", "aim"]):
            return "goals"
        elif any(w in text_lower for w in ["habit", "usually", "always", "every day", "routine"]):
            return "habits"
        elif any(w in text_lower for w in ["feel", "feeling", "emotion", "sad", "happy", "stress"]):
            return "emotional"
        elif any(w in text_lower for w in ["remind", "remember to", "don't forget"]):
            return "reminders"
        elif any(w in text_lower for w in ["like", "love", "favorite", "prefer", "enjoy"]):
            return "preferences"
        else:
            return "long_term"
    
    def clear_all_memories(self):
        """Clear all memories (with confirmation)."""
        self.local_memory["memories"] = {}
        self.short_term = []
        self._save_local_memory()
        gwen_logger.memory("All memories cleared")


# Global memory engine instance
memory = MemoryEngine()