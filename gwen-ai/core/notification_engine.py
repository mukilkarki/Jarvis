"""
notification_engine.py - Smart notification system for Gwen AI
"""

import os
import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

from utils.logger import gwen_logger
from utils.notification_helper import notification_helper
from utils.helpers import load_json, save_json, generate_id


class NotificationEngine:
    """
    Smart notification system for reminders, motivation,
    hydration, study breaks, and quest notifications.
    """
    
    def __init__(self):
        """Initialize notification engine."""
        self.running = False
        self.thread = None
        self.scheduler = schedule.Scheduler()
        
        # Notification settings
        self.settings_path = "data/settings.json"
        self.settings = self._load_settings()
        
        # Active notifications
        self.active_notifications: List[Dict[str, Any]] = []
        
        gwen_logger.system("Notification engine initialized")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load notification settings."""
        defaults = {
            "notifications_enabled": True,
            "motivation_interval": 120,  # minutes
            "hydration_interval": 60,
            "study_reminder": True,
            "sleep_reminder": True,
            "sound_enabled": True,
            "focus_alerts": True,
            "daily_summary": True,
            "last_motivation_time": None,
            "last_hydration_time": None
        }
        
        saved = load_json(self.settings_path)
        return {**defaults, **saved.get("notifications", {})}
    
    def _save_settings(self):
        """Save notification settings."""
        data = load_json(self.settings_path)
        data["notifications"] = self.settings
        save_json(self.settings_path, data)
    
    # ─── NOTIFICATION SCHEDULING ─────────────────────────────────────
    
    def start(self):
        """Start the notification scheduler."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        gwen_logger.system("Notification scheduler started")
    
    def stop(self):
        """Stop the notification scheduler."""
        self.running = False
        gwen_logger.system("Notification scheduler stopped")
    
    def _run_scheduler(self):
        """Run the notification scheduler loop."""
        self._setup_scheduled_notifications()
        
        while self.running:
            self.scheduler.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    def _setup_scheduled_notifications(self):
        """Setup scheduled notification intervals."""
        if self.settings.get("motivation_interval"):
            interval = self.settings["motivation_interval"]
            self.scheduler.every(interval).minutes.do(self.send_motivation)
        
        if self.settings.get("hydration_interval"):
            interval = self.settings["hydration_interval"]
            self.scheduler.every(interval).minutes.do(self.send_hydration_reminder)
        
        # Study reminder at configured times
        if self.settings.get("study_reminder"):
            self.scheduler.every().day.at("09:00").do(self.send_study_reminder)
            self.scheduler.every().day.at("14:00").do(self.send_study_reminder)
            self.scheduler.every().day.at("19:00").do(self.send_study_reminder)
        
        # Sleep reminder
        if self.settings.get("sleep_reminder"):
            self.scheduler.every().day.at("22:00").do(self.send_sleep_reminder)
        
        gwen_logger.debug("Scheduled notifications configured")
    
    # ─── NOTIFICATION TYPES ─────────────────────────────────────────
    
    def send_motivation(self):
        """Send motivational notification."""
        if not self.settings.get("notifications_enabled"):
            return
        
        notification_helper.send_motivation_notification()
        self.settings["last_motivation_time"] = datetime.now().isoformat()
        self._save_settings()
        gwen_logger.system("Sent motivation notification")
    
    def send_hydration_reminder(self):
        """Send hydration reminder."""
        if not self.settings.get("notifications_enabled"):
            return
        
        notification_helper.send_notification(
            "💧 Hydration Time!",
            "Sir, time to drink water! Stay hydrated!",
            "normal"
        )
        self.settings["last_hydration_time"] = datetime.now().isoformat()
        self._save_settings()
        gwen_logger.system("Sent hydration reminder")
    
    def send_study_reminder(self):
        """Send study reminder."""
        if not self.settings.get("notifications_enabled"):
            return
        
        notification_helper.send_notification(
            "📚 Study Time!",
            "Sir, time for a focused study session! Let's level up!",
            "normal"
        )
        gwen_logger.system("Sent study reminder")
    
    def send_sleep_reminder(self):
        """Send sleep reminder."""
        if not self.settings.get("notifications_enabled"):
            return
        
        notification_helper.send_notification(
            "🌙 Time to Rest!",
            "Sir, it's getting late. Your body needs rest for tomorrow!",
            "critical"
        )
        gwen_logger.system("Sent sleep reminder")
    
    def send_quest_notification(self, quest_name: str, xp: int):
        """Send quest completion notification."""
        notification_helper.send_quest_notification(quest_name, xp)
    
    def send_level_up_notification(self, level: int, rank: str):
        """Send level up notification."""
        notification_helper.send_level_up_notification(level, rank)
    
    def send_custom_notification(self, title: str, message: str, urgency: str = "normal"):
        """Send a custom notification."""
        notification_helper.send_notification(title, message, urgency)
    
    # ─── CUSTOM REMINDERS ───────────────────────────────────────────
    
    def set_reminder(self, message: str, delay_minutes: int) -> bool:
        """
        Set a timed reminder.
        
        Args:
            message: Reminder message
            delay_minutes: Minutes from now
        """
        try:
            reminder_time = datetime.now() + timedelta(minutes=delay_minutes)
            
            reminder = {
                "id": generate_id("rem"),
                "message": message,
                "set_at": datetime.now().isoformat(),
                "remind_at": reminder_time.isoformat(),
                "delay_minutes": delay_minutes,
                "completed": False
            }
            
            # Schedule the reminder
            def send_reminder():
                if not reminder["completed"]:
                    notification_helper.send_reminder_notification(
                        message, 
                        reminder_time.strftime("%H:%M")
                    )
                    reminder["completed"] = True
            
            self.scheduler.every(delay_minutes).minutes.do(send_reminder).tag(reminder["id"])
            self.active_notifications.append(reminder)
            
            gwen_logger.system(f"Reminder set: '{message}' in {delay_minutes} minutes")
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to set reminder: {e}")
            return False
    
    def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancel a scheduled reminder."""
        try:
            self.scheduler.clear(reminder_id)
            self.active_notifications = [
                r for r in self.active_notifications if r["id"] != reminder_id
            ]
            gwen_logger.system(f"Reminder cancelled: {reminder_id}")
            return True
        except Exception as e:
            gwen_logger.error(f"Failed to cancel reminder: {e}")
            return False
    
    def get_active_reminders(self) -> List[Dict[str, Any]]:
        """Get all active reminders."""
        return [r for r in self.active_notifications if not r["completed"]]
    
    # ─── SETTINGS ───────────────────────────────────────────────────
    
    def toggle_notifications(self) -> bool:
        """Toggle all notifications on/off."""
        self.settings["notifications_enabled"] = not self.settings["notifications_enabled"]
        self._save_settings()
        
        status = "enabled" if self.settings["notifications_enabled"] else "disabled"
        gwen_logger.system(f"Notifications {status}")
        return self.settings["notifications_enabled"]
    
    def update_interval(self, notification_type: str, interval_minutes: int):
        """Update notification interval."""
        if notification_type == "motivation":
            self.settings["motivation_interval"] = interval_minutes
        elif notification_type == "hydration":
            self.settings["hydration_interval"] = interval_minutes
        
        self._save_settings()
        # Restart scheduler to apply changes
        self.stop()
        self.start()
        gwen_logger.system(f"{notification_type} interval updated to {interval_minutes} minutes")


# Global notification engine instance
notifications = NotificationEngine()