"""
notification_helper.py - Desktop notification helper for Gwen AI
"""

import os
import subprocess
import platform
from datetime import datetime
from typing import Optional

from utils.logger import gwen_logger


class NotificationHelper:
    """Cross-platform desktop notification system."""
    
    @staticmethod
    def send_notification(title: str, message: str, urgency: str = "normal") -> bool:
        """
        Send a desktop notification.
        
        Args:
            title: Notification title
            message: Notification body
            urgency: 'low', 'normal', or 'critical'
        """
        try:
            system = platform.system().lower()
            
            if system == "linux":
                return NotificationHelper._linux_notify(title, message, urgency)
            elif system == "darwin":
                return NotificationHelper._mac_notify(title, message)
            elif system == "windows":
                return NotificationHelper._windows_notify(title, message)
            else:
                gwen_logger.warning(f"Unsupported OS for notifications: {system}")
                return False
                
        except Exception as e:
            gwen_logger.error(f"Notification failed: {e}")
            return False
    
    @staticmethod
    def _linux_notify(title: str, message: str, urgency: str) -> bool:
        """Linux notification via notify-send."""
        try:
            urgency_map = {"low": "low", "normal": "normal", "critical": "critical"}
            urg = urgency_map.get(urgency, "normal")
            
            subprocess.run(
                ["notify-send", "-u", urg, "-a", "Gwen AI", title, message],
                timeout=5, capture_output=True
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            gwen_logger.debug(f"notify-send failed: {e}")
            return False
    
    @staticmethod
    def _mac_notify(title: str, message: str) -> bool:
        """macOS notification via osascript."""
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], timeout=5, capture_output=True)
            return True
        except Exception as e:
            gwen_logger.debug(f"macOS notification failed: {e}")
            return False
    
    @staticmethod
    def _windows_notify(title: str, message: str) -> bool:
        """Windows notification via PowerShell."""
        try:
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $textNodes = $template.GetElementsByTagName("text")
            $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
            $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier().Show($toast)
            '''
            subprocess.run(["powershell", "-Command", ps_script], timeout=5, capture_output=True)
            return True
        except Exception as e:
            gwen_logger.debug(f"Windows notification failed: {e}")
            return False
    
    @staticmethod
    def send_motivation_notification():
        """Send a motivational notification."""
        messages = [
            ("💪 Stay Strong!", "You're doing great sir! Keep pushing forward!"),
            ("🌟 You Got This!", "Remember why you started, sir. Success is near!"),
            ("🚀 Level Up!", "Another day, another opportunity to grow, sir!"),
            ("⚡ Stay Focused!", "Great things take time. Keep going, sir!"),
            ("🎯 Stay on Track!", "Your future self will thank you for your efforts today!")
        ]
        
        import random
        title, message = random.choice(messages)
        NotificationHelper.send_notification(title, message, "normal")
    
    @staticmethod
    def send_reminder_notification(task: str, time_str: str):
        """Send a reminder notification."""
        title = "⏰ Reminder"
        message = f"Sir, remember to {task} at {time_str}"
        NotificationHelper.send_notification(title, message, "normal")
    
    @staticmethod
    def send_quest_notification(quest_name: str, xp_reward: int):
        """Send a quest notification."""
        title = "⚔️ New Quest Available!"
        message = f"{quest_name} | Reward: {xp_reward} XP"
        NotificationHelper.send_notification(title, message, "normal")
    
    @staticmethod
    def send_level_up_notification(new_level: int, rank: str):
        """Send level up notification."""
        title = "🎉 LEVEL UP!"
        message = f"Congratulations sir! You reached Level {new_level} - {rank}!"
        NotificationHelper.send_notification(title, message, "critical")


# Global notification helper instance
notification_helper = NotificationHelper()