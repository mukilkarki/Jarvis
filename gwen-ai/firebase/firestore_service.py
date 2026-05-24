"""
firestore_service.py - Firebase Firestore service for Gwen AI
"""

import json
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable

from utils.logger import gwen_logger
from firebase.firebase_config import COLLECTIONS, SUBCOLLECTIONS, validate_firebase_config, get_firebase_credential_path


class FirestoreService:
    """
    Firebase Firestore service for data persistence.
    Handles all database operations with fallback to local storage.
    """
    
    def __init__(self):
        """Initialize Firestore service."""
        self.db = None
        self.initialized = False
        self.local_fallback = {}
        self._init_firebase()
    
    def _init_firebase(self):
        """Initialize Firebase connection."""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            cred_path = get_firebase_credential_path()
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.initialized = True
                gwen_logger.system("Firebase Firestore connected successfully")
            else:
                gwen_logger.warning("Firebase credentials not available. Using local storage fallback.")
        except Exception as e:
            gwen_logger.warning(f"Firebase initialization failed: {e}. Using local storage fallback.")
    
    def _get_collection(self, collection_name: str):
        """Get a Firestore collection reference."""
        if self.db and self.initialized:
            return self.db.collection(collection_name)
        return None
    
    # ─── MEMORY OPERATIONS ───────────────────────────────────────────
    
    def save_memory(self, memory: Dict[str, Any]) -> bool:
        """Save a memory to Firestore."""
        try:
            memory["updated_at"] = datetime.now().isoformat()
            
            if self.initialized:
                collection = self._get_collection(COLLECTIONS["memories"])
                doc_id = memory.get("id", str(datetime.now().timestamp()))
                collection.document(doc_id).set(memory)
                gwen_logger.memory(f"Memory saved to Firestore: {memory.get('content', '')[:50]}...")
            else:
                # Local fallback
                key = f"memory_{memory.get('id', str(datetime.now().timestamp()))}"
                self.local_fallback[key] = memory
                gwen_logger.memory("Memory saved locally (Firestore fallback)")
            
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to save memory: {e}")
            return False
    
    def get_memories(self, memory_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve memories with optional type filter."""
        memories = []
        try:
            if self.initialized:
                collection = self._get_collection(COLLECTIONS["memories"])
                query = collection.order_by("updated_at", direction="DESCENDING")
                
                if memory_type:
                    query = query.where("type", "==", memory_type)
                
                docs = query.limit(limit).stream()
                memories = [{**doc.to_dict(), "id": doc.id} for doc in docs]
            else:
                # Local fallback
                memories = [
                    v for k, v in self.local_fallback.items()
                    if k.startswith("memory_") and (not memory_type or v.get("type") == memory_type)
                ]
                memories = sorted(memories, key=lambda x: x.get("updated_at", ""), reverse=True)[:limit]
        except Exception as e:
            gwen_logger.error(f"Failed to retrieve memories: {e}")
        
        return memories
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        try:
            if self.initialized:
                self._get_collection(COLLECTIONS["memories"]).document(memory_id).delete()
            else:
                key = f"memory_{memory_id}"
                self.local_fallback.pop(key, None)
            
            gwen_logger.memory(f"Memory deleted: {memory_id}")
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to delete memory: {e}")
            return False
    
    # ─── PRODUCTIVITY OPERATIONS ─────────────────────────────────────
    
    def save_productivity(self, data: Dict[str, Any]) -> bool:
        """Save productivity data."""
        try:
            data["updated_at"] = datetime.now().isoformat()
            
            if self.initialized:
                doc_id = data.get("user_id", "default")
                self._get_collection(COLLECTIONS["productivity"]).document(doc_id).set(data, merge=True)
            else:
                self.local_fallback["productivity"] = data
            
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to save productivity data: {e}")
            return False
    
    def get_productivity(self, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """Get productivity data."""
        try:
            if self.initialized:
                doc = self._get_collection(COLLECTIONS["productivity"]).document(user_id).get()
                return doc.to_dict() if doc.exists else None
            else:
                return self.local_fallback.get("productivity")
        except Exception as e:
            gwen_logger.error(f"Failed to get productivity data: {e}")
            return None
    
    # ─── REMINDER OPERATIONS ─────────────────────────────────────────
    
    def save_reminder(self, reminder: Dict[str, Any]) -> bool:
        """Save a reminder."""
        try:
            reminder["created_at"] = datetime.now().isoformat()
            reminder["active"] = True
            
            if self.initialized:
                doc_id = reminder.get("id", str(datetime.now().timestamp()))
                self._get_collection(COLLECTIONS["reminders"]).document(doc_id).set(reminder)
            else:
                key = f"reminder_{reminder.get('id', str(datetime.now().timestamp()))}"
                self.local_fallback[key] = reminder
            
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to save reminder: {e}")
            return False
    
    def get_active_reminders(self) -> List[Dict[str, Any]]:
        """Get all active reminders."""
        reminders = []
        try:
            if self.initialized:
                docs = self._get_collection(COLLECTIONS["reminders"]).where("active", "==", True).stream()
                reminders = [{**doc.to_dict(), "id": doc.id} for doc in docs]
            else:
                reminders = [
                    v for k, v in self.local_fallback.items()
                    if k.startswith("reminder_") and v.get("active")
                ]
        except Exception as e:
            gwen_logger.error(f"Failed to get reminders: {e}")
        
        return reminders
    
    def complete_reminder(self, reminder_id: str) -> bool:
        """Mark a reminder as completed."""
        try:
            if self.initialized:
                self._get_collection(COLLECTIONS["reminders"]).document(reminder_id).update({"active": False})
            else:
                key = f"reminder_{reminder_id}"
                if key in self.local_fallback:
                    self.local_fallback[key]["active"] = False
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to complete reminder: {e}")
            return False
    
    # ─── SETTINGS OPERATIONS ─────────────────────────────────────────
    
    def save_setting(self, key: str, value: Any) -> bool:
        """Save a setting."""
        try:
            if self.initialized:
                self._get_collection(COLLECTIONS["settings"]).document(key).set({"value": value, "updated_at": datetime.now().isoformat()})
            else:
                if "settings" not in self.local_fallback:
                    self.local_fallback["settings"] = {}
                self.local_fallback["settings"][key] = value
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to save setting: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        try:
            if self.initialized:
                doc = self._get_collection(COLLECTIONS["settings"]).document(key).get()
                return doc.to_dict().get("value") if doc.exists else default
            else:
                return self.local_fallback.get("settings", {}).get(key, default)
        except Exception as e:
            gwen_logger.error(f"Failed to get setting: {e}")
            return default
    
    # ─── CONVERSATION LOGGING ────────────────────────────────────────
    
    def log_conversation(self, user_input: str, ai_response: str, emotion: Optional[str] = None):
        """Log a conversation entry."""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "ai_response": ai_response,
                "emotion": emotion
            }
            
            if self.initialized:
                self._get_collection(COLLECTIONS["conversations"]).add(entry)
            else:
                if "conversations" not in self.local_fallback:
                    self.local_fallback["conversations"] = []
                self.local_fallback["conversations"].append(entry)
                # Keep only last 1000
                self.local_fallback["conversations"] = self.local_fallback["conversations"][-1000:]
        except Exception as e:
            gwen_logger.error(f"Failed to log conversation: {e}")
    
    # ─── STATS OPERATIONS ────────────────────────────────────────────
    
    def update_stats(self, stats_update: Dict[str, Any]):
        """Update stats."""
        try:
            if self.initialized:
                self._get_collection(COLLECTIONS["stats"]).document("user_stats").set(stats_update, merge=True)
            else:
                if "stats" not in self.local_fallback:
                    self.local_fallback["stats"] = {}
                self.local_fallback["stats"].update(stats_update)
        except Exception as e:
            gwen_logger.error(f"Failed to update stats: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get user stats."""
        try:
            if self.initialized:
                doc = self._get_collection(COLLECTIONS["stats"]).document("user_stats").get()
                return doc.to_dict() if doc.exists else {}
            else:
                return self.local_fallback.get("stats", {})
        except Exception as e:
            gwen_logger.error(f"Failed to get stats: {e}")
            return {}


# Global Firestore service instance
firestore = FirestoreService()