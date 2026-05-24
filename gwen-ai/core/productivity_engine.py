"""
productivity_engine.py - Solo Leveling inspired productivity system for Gwen AI
"""

import os
import json
import random
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple

from utils.logger import gwen_logger
from utils.helpers import load_json, save_json, generate_id
from firebase.firestore_service import firestore


class ProductivityEngine:
    """
    Solo Leveling inspired productivity system with XP, levels, 
    quests, streaks, and achievements.
    """
    
    # Rank system inspired by Solo Leveling
    RANKS = [
        {"name": "E-Rank", "level_range": (1, 5), "title": "Beginner Hunter"},
        {"name": "D-Rank", "level_range": (6, 10), "title": "Apprentice Hunter"},
        {"name": "C-Rank", "level_range": (11, 20), "title": "Advanced Hunter"},
        {"name": "B-Rank", "level_range": (21, 35), "title": "Elite Hunter"},
        {"name": "A-Rank", "level_range": (36, 50), "title": "Master Hunter"},
        {"name": "S-Rank", "level_range": (51, 70), "title": "Legendary Hunter"},
        {"name": "SS-Rank", "level_range": (71, 85), "title": "Mythic Hunter"},
        {"name": "SSS-Rank", "level_range": (86, 100), "title": "Shadow Monarch"}
    ]
    
    # Daily quest templates
    DAILY_QUESTS = [
        {"name": "Focus Session", "description": "Complete a 25-minute focus session", "xp": 50, "type": "focus"},
        {"name": "Study Time", "description": "Study for 1 hour", "xp": 75, "type": "study"},
        {"name": "Code Warrior", "description": "Write code for 30 minutes", "xp": 60, "type": "coding"},
        {"name": "Reading Quest", "description": "Read for 20 minutes", "xp": 40, "type": "reading"},
        {"name": "Hydration Check", "description": "Drink 8 glasses of water", "xp": 20, "type": "health"},
        {"name": "Task Master", "description": "Complete 5 tasks from your todo list", "xp": 80, "type": "productivity"},
        {"name": "Morning Routine", "description": "Complete morning routine", "xp": 30, "type": "routine"},
        {"name": "Exercise", "description": "Exercise for 15 minutes", "xp": 45, "type": "health"},
        {"name": "Learning", "description": "Learn something new for 30 min", "xp": 55, "type": "learning"},
        {"name": "Social Quest", "description": "Connect with someone", "xp": 35, "type": "social"}
    ]
    
    # Achievement definitions
    ACHIEVEMENTS = {
        "first_quest": {"name": "First Steps", "description": "Complete your first quest", "icon": "🌟"},
        "streak_3": {"name": "Consistent", "description": "3-day streak", "icon": "🔥"},
        "streak_7": {"name": "Determined", "description": "7-day streak", "icon": "💪"},
        "streak_30": {"name": "Unstoppable", "description": "30-day streak", "icon": "⚔️"},
        "level_5": {"name": "Rising Hunter", "description": "Reach Level 5", "icon": "⬆️"},
        "level_10": {"name": "Apprentice", "description": "Reach Level 10", "icon": "🎯"},
        "level_25": {"name": "Elite Status", "description": "Reach Level 25", "icon": "👑"},
        "level_50": {"name": "Master Hunter", "description": "Reach Level 50", "icon": "🏆"},
        "quest_10": {"name": "Quest Addict", "description": "Complete 10 quests", "icon": "📋"},
        "quest_50": {"name": "Quest Legend", "description": "Complete 50 quests", "icon": "💎"},
        "xp_1000": {"name": "XP Collector", "description": "Earn 1000 XP", "icon": "⚡"},
        "xp_10000": {"name": "XP Master", "description": "Earn 10000 XP", "icon": "✨"},
        "focus_5": {"name": "Focused Mind", "description": "Complete 5 focus sessions", "icon": "🧠"},
        "focus_20": {"name": "Zen Master", "description": "Complete 20 focus sessions", "icon": "🧘"},
        "perfect_day": {"name": "Perfect Day", "description": "Complete all daily quests", "icon": "💯"}
    }
    
    def __init__(self):
        """Initialize productivity engine."""
        self.data_path = "data/quests.json"
        self.stats_path = "data/stats.json"
        self.data = self._load_data()
        self.stats = self._load_stats()
        
        # Ensure daily quests are generated
        self._ensure_daily_quests()
        
        gwen_logger.system("Productivity engine initialized")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load productivity data."""
        return load_json(self.data_path)
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load stats data."""
        return load_json(self.stats_path)
    
    def _save_data(self):
        """Save productivity data."""
        save_json(self.data_path, self.data)
    
    def _save_stats(self):
        """Save stats data."""
        save_json(self.stats_path, self.stats)
    
    def _ensure_daily_quests(self):
        """Generate daily quests if not already created for today."""
        today = date.today().isoformat()
        
        if self.data.get("quest_date") != today:
            # Select 3 random daily quests
            quests = random.sample(self.DAILY_QUESTS, min(3, len(self.DAILY_QUESTS)))
            self.data["quest_date"] = today
            self.data["daily_quests"] = [
                {**quest, "id": generate_id("q"), "completed": False, "date": today}
                for quest in quests
            ]
            self.data["quests_completed_today"] = 0
            self._save_data()
            gwen_logger.system("Daily quests generated")
    
    # ─── RANK & LEVEL SYSTEM ────────────────────────────────────────
    
    def get_level(self) -> int:
        """Get current level."""
        return max(1, self.stats.get("level", 1))
    
    def get_xp(self) -> int:
        """Get current XP."""
        return self.stats.get("xp", 0)
    
    def get_xp_to_next_level(self) -> int:
        """Get XP needed for next level."""
        level = self.get_level()
        return level * 100  # Each level requires more XP
    
    def get_rank(self) -> Dict[str, Any]:
        """Get current rank based on level."""
        level = self.get_level()
        
        for rank in self.RANKS:
            if rank["level_range"][0] <= level <= rank["level_range"][1]:
                return rank
        
        return self.RANKS[-1]  # Max rank
    
    def add_xp(self, amount: int) -> List[str]:
        """
        Add XP and handle level-ups.
        Returns list of events (level-ups, achievements).
        """
        events = []
        self.stats["xp"] = self.stats.get("xp", 0) + amount
        self.stats["total_xp"] = self.stats.get("total_xp", 0) + amount
        
        # Check for XP achievements
        total_xp = self.stats["total_xp"]
        if total_xp >= 1000 and not self.stats.get("achievements", {}).get("xp_1000"):
            self._unlock_achievement("xp_1000")
            events.append("achievement_xp_1000")
        if total_xp >= 10000 and not self.stats.get("achievements", {}).get("xp_10000"):
            self._unlock_achievement("xp_10000")
            events.append("achievement_xp_10000")
        
        # Check for level ups
        while self.stats["xp"] >= self.get_xp_to_next_level():
            self.stats["xp"] -= self.get_xp_to_next_level()
            self.stats["level"] = self.stats.get("level", 1) + 1
            new_level = self.stats["level"]
            
            events.append(f"level_up_{new_level}")
            
            # Check level achievements
            if new_level >= 5 and not self.stats.get("achievements", {}).get("level_5"):
                self._unlock_achievement("level_5")
            if new_level >= 10 and not self.stats.get("achievements", {}).get("level_10"):
                self._unlock_achievement("level_10")
            if new_level >= 25 and not self.stats.get("achievements", {}).get("level_25"):
                self._unlock_achievement("level_25")
            if new_level >= 50 and not self.stats.get("achievements", {}).get("level_50"):
                self._unlock_achievement("level_50")
        
        self._save_stats()
        self._sync_to_firestore()
        
        return events
    
    # ─── QUESTS ─────────────────────────────────────────────────────
    
    def get_daily_quests(self) -> List[Dict[str, Any]]:
        """Get today's daily quests."""
        self._ensure_daily_quests()
        return self.data.get("daily_quests", [])
    
    def complete_quest(self, quest_id: str) -> Tuple[bool, str, int]:
        """
        Mark a quest as completed and award XP.
        Returns (success, message, xp_earned).
        """
        quests = self.data.get("daily_quests", [])
        
        for quest in quests:
            if quest["id"] == quest_id and not quest["completed"]:
                quest["completed"] = True
                quest["completed_at"] = datetime.now().isoformat()
                
                xp_earned = quest.get("xp", 50)
                events = self.add_xp(xp_earned)
                
                # Update stats
                self.data["quests_completed_today"] = self.data.get("quests_completed_today", 0) + 1
                self.stats["total_quests"] = self.stats.get("total_quests", 0) + 1
                
                # Streak update
                self._update_streak()
                
                # Check achievements
                total_quests = self.stats["total_quests"]
                if total_quests >= 1 and not self.stats.get("achievements", {}).get("first_quest"):
                    self._unlock_achievement("first_quest")
                    events.append("achievement_first_quest")
                if total_quests >= 10 and not self.stats.get("achievements", {}).get("quest_10"):
                    self._unlock_achievement("quest_10")
                    events.append("achievement_quest_10")
                if total_quests >= 50 and not self.stats.get("achievements", {}).get("quest_50"):
                    self._unlock_achievement("quest_50")
                    events.append("achievement_quest_50")
                
                # Perfect day check
                all_completed = all(q["completed"] for q in quests)
                if all_completed and not self.stats.get("achievements", {}).get("perfect_day"):
                    self._unlock_achievement("perfect_day")
                    events.append("achievement_perfect_day")
                
                self._save_data()
                self._save_stats()
                self._sync_to_firestore()
                
                return True, f"+{xp_earned} XP for completing '{quest['name']}'!", xp_earned
        
        return False, "Quest not found or already completed.", 0
    
    # ─── STREAK SYSTEM ──────────────────────────────────────────────
    
    def get_streak(self) -> int:
        """Get current streak."""
        return self.stats.get("streak", 0)
    
    def get_longest_streak(self) -> int:
        """Get longest streak."""
        return self.stats.get("longest_streak", 0)
    
    def _update_streak(self):
        """Update streak tracking."""
        today = date.today()
        last_active = self.stats.get("last_active_date")
        
        if last_active:
            last_date = date.fromisoformat(last_active)
            diff = (today - last_date).days
            
            if diff == 1:  # Consecutive day
                self.stats["streak"] = self.stats.get("streak", 0) + 1
            elif diff > 1:  # Streak broken
                self.stats["streak"] = 1
            # diff == 0 means already active today
        else:
            self.stats["streak"] = 1
        
        # Update longest streak
        current_streak = self.stats.get("streak", 0)
        if current_streak > self.stats.get("longest_streak", 0):
            self.stats["longest_streak"] = current_streak
        
        self.stats["last_active_date"] = today.isoformat()
        
        # Check streak achievements
        if current_streak >= 3 and not self.stats.get("achievements", {}).get("streak_3"):
            self._unlock_achievement("streak_3")
        if current_streak >= 7 and not self.stats.get("achievements", {}).get("streak_7"):
            self._unlock_achievement("streak_7")
        if current_streak >= 30 and not self.stats.get("achievements", {}).get("streak_30"):
            self._unlock_achievement("streak_30")
    
    # ─── FOCUS SESSIONS ─────────────────────────────────────────────
    
    def start_focus_session(self) -> Dict[str, Any]:
        """Start a focus session."""
        session = {
            "id": generate_id("focus"),
            "start_time": datetime.now().isoformat(),
            "duration_minutes": 25,  # Pomodoro default
            "active": True
        }
        
        if "focus_sessions" not in self.data:
            self.data["focus_sessions"] = []
        self.data["focus_sessions"].append(session)
        self._save_data()
        
        gwen_logger.system("Focus session started")
        return session
    
    def complete_focus_session(self, session_id: str, duration: int = 25) -> int:
        """
        Complete a focus session and award XP.
        Returns XP earned.
        """
        sessions = self.data.get("focus_sessions", [])
        
        for session in sessions:
            if session.get("id") == session_id and session.get("active"):
                session["active"] = False
                session["end_time"] = datetime.now().isoformat()
                session["actual_duration"] = duration
                
                # Award XP (2 XP per minute)
                xp_earned = duration * 2
                self.add_xp(xp_earned)
                
                # Update stats
                self.stats["focus_sessions"] = self.stats.get("focus_sessions", 0) + 1
                total_focus = self.stats["focus_sessions"]
                
                # Check focus achievements
                if total_focus >= 5 and not self.stats.get("achievements", {}).get("focus_5"):
                    self._unlock_achievement("focus_5")
                if total_focus >= 20 and not self.stats.get("achievements", {}).get("focus_20"):
                    self._unlock_achievement("focus_20")
                
                self._save_data()
                self._save_stats()
                
                return xp_earned
        
        return 0
    
    # ─── ACHIEVEMENTS ───────────────────────────────────────────────
    
    def _unlock_achievement(self, achievement_id: str):
        """Unlock an achievement."""
        if achievement_id in self.ACHIEVEMENTS:
            if "achievements" not in self.stats:
                self.stats["achievements"] = {}
            
            if achievement_id not in self.stats["achievements"]:
                achievement = self.ACHIEVEMENTS[achievement_id]
                self.stats["achievements"][achievement_id] = {
                    "unlocked_at": datetime.now().isoformat(),
                    "name": achievement["name"],
                    "description": achievement["description"],
                    "icon": achievement["icon"]
                }
                gwen_logger.system(f"Achievement unlocked: {achievement['name']}")
    
    def get_achievements(self) -> Dict[str, Any]:
        """Get unlocked achievements."""
        return self.stats.get("achievements", {})
    
    def get_all_achievement_defs(self) -> Dict[str, Any]:
        """Get all achievement definitions."""
        return self.ACHIEVEMENTS
    
    # ─── STATS & PROGRESS ───────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive productivity stats."""
        level = self.get_level()
        rank = self.get_rank()
        
        return {
            "level": level,
            "xp": self.get_xp(),
            "xp_to_next": self.get_xp_to_next_level(),
            "xp_progress": round((self.get_xp() / self.get_xp_to_next_level()) * 100, 1),
            "rank": rank["name"],
            "rank_title": rank["title"],
            "streak": self.get_streak(),
            "longest_streak": self.get_longest_streak(),
            "total_quests": self.stats.get("total_quests", 0),
            "quests_today": self.data.get("quests_completed_today", 0),
            "focus_sessions": self.stats.get("focus_sessions", 0),
            "total_xp": self.stats.get("total_xp", 0),
            "achievements": len(self.get_achievements()),
            "total_achievements": len(self.ACHIEVEMENTS)
        }
    
    def get_motivational_message(self) -> str:
        """Get a motivational message based on current stats."""
        level = self.get_level()
        rank = self.get_rank()
        streak = self.get_streak()
        
        if streak >= 30:
            return f"Sir! You're on a {streak}-day streak! You're absolutely unstoppable! Shadow Monarch level dedication! ⚔️"
        elif streak >= 7:
            return f"Sir! {streak}-day streak! You're building incredible momentum! Keep going! 🔥"
        elif streak >= 3:
            return f"Nice streak sir! {streak} days and counting! You're leveling up! 💪"
        elif streak == 0:
            if level > 1:
                return f"Sir, you're already Level {level} {rank['name']}! Let's start today's quests and get that streak going! ⚔️"
            else:
                return f"Ready to begin your journey sir? Let's start with some quests and level up together! 🌟"
        else:
            return f"Sir, you're on day {streak}! Let's keep the momentum going! 🚀"
    
    def get_progress_report(self) -> str:
        """Get a detailed progress report."""
        stats = self.get_stats()
        
        report = f"""
╔══════════════════════════════════╗
║     ★ LEVEL & RANK PROGRESS ★    ║
╠══════════════════════════════════╣
║ Level: {stats['level']:<3} | Rank: {stats['rank']:<8} ║
║ Title: {stats['rank_title']:<19} ║
║ XP: {stats['xp']:<5} / {stats['xp_to_next']:<5} ({stats['xp_progress']}%)     ║
╠══════════════════════════════════╣
║ ★ STATS ★                        ║
║ Streak: {stats['streak']:<3} days  | Longest: {stats['longest_streak']:<3}     ║
║ Total XP: {stats['total_xp']:<6} | Quests: {stats['total_quests']:<3}      ║
║ Focus Sessions: {stats['focus_sessions']:<3}     ║
║ Achievements: {stats['achievements']:<2} / {stats['total_achievements']:<2}            ║
╚══════════════════════════════════╝
"""
        return report
    
    def _sync_to_firestore(self):
        """Sync productivity data to Firestore."""
        try:
            firestore.save_productivity({
                "user_id": "default",
                "level": self.get_level(),
                "xp": self.get_xp(),
                "streak": self.get_streak(),
                "stats": self.stats
            })
        except Exception as e:
            gwen_logger.debug(f"Firestore sync failed: {e}")


# Global productivity engine instance
productivity = ProductivityEngine()