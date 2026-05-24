"""
automation_engine.py - PC automation engine for Gwen AI
"""

import os
import sys
import subprocess
import platform
import webbrowser
from datetime import datetime
from typing import Optional, Tuple, Dict, List, Callable

from utils.logger import gwen_logger


class AutomationEngine:
    """
    PC automation engine that handles system commands.
    Controls apps, websites, system functions, and media.
    """
    
    def __init__(self):
        """Initialize automation engine."""
        self.system = platform.system().lower()
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.last_command_time = datetime.now()
        
        # App mappings for different OS
        self.apps = self._get_app_mappings()
        
        # Website shortcuts
        self.websites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com",
            "reddit": "https://www.reddit.com",
            "stackoverflow": "https://stackoverflow.com",
            "twitter": "https://twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "whatsapp": "https://web.whatsapp.com",
            "chatgpt": "https://chat.openai.com",
            "deepseek": "https://chat.deepseek.com",
            "claude": "https://claude.ai"
        }
        
        gwen_logger.automation(f"Automation engine initialized ({self.system})")
    
    def _get_app_mappings(self) -> Dict[str, Dict[str, str]]:
        """Get app launch commands for the current OS."""
        if self.system == "windows":
            return {
                "chrome": {"cmd": "start chrome", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"},
                "notepad": {"cmd": "notepad", "path": "notepad.exe"},
                "calculator": {"cmd": "calc", "path": "calc.exe"},
                "explorer": {"cmd": "explorer", "path": "explorer.exe"},
                "cmd": {"cmd": "cmd", "path": "cmd.exe"},
                "powershell": {"cmd": "powershell", "path": "powershell.exe"},
                "vscode": {"cmd": "code", "path": "code.cmd"},
                "spotify": {"cmd": "start spotify", "path": ""},
                "vlc": {"cmd": "start vlc", "path": ""}
            }
        elif self.system == "darwin":  # macOS
            return {
                "chrome": {"cmd": "open -a 'Google Chrome'", "path": ""},
                "safari": {"cmd": "open -a Safari", "path": ""},
                "terminal": {"cmd": "open -a Terminal", "path": ""},
                "vscode": {"cmd": "code", "path": ""},
                "spotify": {"cmd": "open -a Spotify", "path": ""},
                "finder": {"cmd": "open -a Finder", "path": ""}
            }
        else:  # Linux
            return {
                "chrome": {"cmd": "google-chrome", "path": ""},
                "firefox": {"cmd": "firefox", "path": ""},
                "terminal": {"cmd": "gnome-terminal", "path": ""},
                "vscode": {"cmd": "code", "path": ""},
                "calculator": {"cmd": "gnome-calculator", "path": ""},
                "files": {"cmd": "nautilus", "path": ""},
                "spotify": {"cmd": "spotify", "path": ""}
            }
    
    # ─── APPLICATION CONTROL ────────────────────────────────────────
    
    def open_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Open an application.
        
        Args:
            app_name: Name of the application
        
        Returns:
            (success, message)
        """
        app_name = app_name.lower().strip()
        
        # Check app mappings
        if app_name in self.apps:
            try:
                cmd = self.apps[app_name]["cmd"]
                subprocess.Popen(cmd, shell=True)
                gwen_logger.automation(f"Opened app: {app_name}")
                return True, f"Opening {app_name} sir!"
            except Exception as e:
                gwen_logger.error(f"Failed to open {app_name}: {e}")
                return False, f"Sorry sir, I couldn't open {app_name}."
        
        # Try to find and launch
        try:
            if self.system == "windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif self.system == "darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
            
            gwen_logger.automation(f"Opened app: {app_name}")
            return True, f"Opening {app_name} sir!"
        except Exception as e:
            gwen_logger.error(f"Failed to open {app_name}: {e}")
            return False, f"Sorry sir, {app_name} not found."
    
    def close_app(self, app_name: str) -> Tuple[bool, str]:
        """Close an application."""
        app_name = app_name.lower().strip()
        try:
            if self.system == "windows":
                subprocess.run(f"taskkill /f /im {app_name}.exe", shell=True, capture_output=True)
            elif self.system == "darwin":
                subprocess.run(["pkill", "-f", app_name])
            else:
                subprocess.run(["pkill", "-f", app_name])
            
            gwen_logger.automation(f"Closed app: {app_name}")
            return True, f"Closed {app_name} sir!"
        except Exception as e:
            gwen_logger.error(f"Failed to close {app_name}: {e}")
            return False, f"Could not close {app_name}."
    
    # ─── WEBSITE CONTROL ────────────────────────────────────────────
    
    def open_website(self, url: str) -> Tuple[bool, str]:
        """
        Open a website in default browser.
        
        Args:
            url: URL or website name
        """
        # Check shortcuts
        if url.lower() in self.websites:
            url = self.websites[url.lower()]
        elif not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        try:
            webbrowser.open(url)
            gwen_logger.automation(f"Opened website: {url}")
            return True, f"Opening {url} sir!"
        except Exception as e:
            gwen_logger.error(f"Failed to open website: {e}")
            return False, "Could not open website sir."
    
    def search_google(self, query: str) -> Tuple[bool, str]:
        """Search Google for a query."""
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            gwen_logger.automation(f"Google search: {query}")
            return True, f"Searching Google for '{query}' sir!"
        except Exception as e:
            gwen_logger.error(f"Search failed: {e}")
            return False, "Search failed sir."
    
    def open_youtube(self, query: Optional[str] = None) -> Tuple[bool, str]:
        """Open YouTube or search for a video."""
        try:
            if query:
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            else:
                url = "https://www.youtube.com"
            
            webbrowser.open(url)
            gwen_logger.automation(f"Opening YouTube: {query or 'home'}")
            return True, f"Opening YouTube sir!"
        except Exception as e:
            gwen_logger.error(f"YouTube error: {e}")
            return False, "Could not open YouTube."
    
    # ─── SYSTEM CONTROL ─────────────────────────────────────────────
    
    def lock_screen(self) -> Tuple[bool, str]:
        """Lock the computer screen."""
        try:
            if self.system == "windows":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation")
            elif self.system == "darwin":
                subprocess.run(["pmset", "displaysleepnow"])
            else:  # Linux
                subprocess.run(["gnome-screensaver-command", "-l"])
            
            gwen_logger.automation("Screen locked")
            return True, "Locking screen sir! Stay safe."
        except Exception as e:
            gwen_logger.error(f"Lock screen failed: {e}")
            return False, "Could not lock screen sir."
    
    def shutdown(self, delay: int = 60) -> Tuple[bool, str]:
        """Shutdown the computer after a delay."""
        try:
            if self.system == "windows":
                subprocess.run(f"shutdown /s /t {delay}")
            elif self.system == "darwin":
                subprocess.run(["sudo", "shutdown", f"-h +{delay // 60}"])
            else:
                subprocess.run(["shutdown", f"+{delay // 60}"])
            
            gwen_logger.automation(f"Shutdown scheduled in {delay}s")
            return True, f"Shutting down in {delay // 60} minutes sir!"
        except Exception as e:
            gwen_logger.error(f"Shutdown failed: {e}")
            return False, "Could not shutdown sir."
    
    def cancel_shutdown(self) -> Tuple[bool, str]:
        """Cancel scheduled shutdown."""
        try:
            if self.system == "windows":
                subprocess.run("shutdown /a")
            elif self.system == "darwin" or self.system == "linux":
                subprocess.run(["shutdown", "-c"])
            
            return True, "Cancelled shutdown sir!"
        except Exception as e:
            gwen_logger.error(f"Cancel shutdown failed: {e}")
            return False, "Could not cancel shutdown."
    
    # ─── MEDIA CONTROL ──────────────────────────────────────────────
    
    def volume_up(self, amount: int = 5) -> Tuple[bool, str]:
        """Increase system volume."""
        try:
            if self.system == "linux":
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{amount}%"])
            elif self.system == "darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) + {amount})"])
            else:
                # Windows - use pyautogui
                import pyautogui
                pyautogui.press("volumeup", presses=amount // 2)
            
            gwen_logger.automation(f"Volume up by {amount}%")
            return True, f"Volume increased sir!"
        except Exception as e:
            gwen_logger.debug(f"Volume up failed: {e}")
            return False, "Could not adjust volume."
    
    def volume_down(self, amount: int = 5) -> Tuple[bool, str]:
        """Decrease system volume."""
        try:
            if self.system == "linux":
                subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{amount}%"])
            elif self.system == "darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) - {amount})"])
            else:
                import pyautogui
                pyautogui.press("volumedown", presses=amount // 2)
            
            gwen_logger.automation(f"Volume down by {amount}%")
            return True, f"Volume decreased sir!"
        except Exception as e:
            gwen_logger.debug(f"Volume down failed: {e}")
            return False, "Could not adjust volume."
    
    def mute(self) -> Tuple[bool, str]:
        """Mute system audio."""
        try:
            if self.system == "linux":
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"])
            elif self.system == "darwin":
                subprocess.run(["osascript", "-e", "set volume output volume 0"])
            else:
                import pyautogui
                pyautogui.press("volumemute")
            
            gwen_logger.automation("System muted")
            return True, "Muted sir!"
        except Exception as e:
            gwen_logger.debug(f"Mute failed: {e}")
            return False, "Could not mute."
    
    def unmute(self) -> Tuple[bool, str]:
        """Unmute system audio."""
        try:
            if self.system == "linux":
                subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])
            elif self.system == "darwin":
                subprocess.run(["osascript", "-e", "set volume output volume 50"])
            else:
                import pyautogui
                pyautogui.press("volumemute")
            
            gwen_logger.automation("System unmuted")
            return True, "Unmuted sir!"
        except Exception as e:
            gwen_logger.debug(f"Unmute failed: {e}")
            return False, "Could not unmute."
    
    # ─── SCREENSHOT ─────────────────────────────────────────────────
    
    def take_screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """Take a screenshot and save it."""
        try:
            import pyautogui
            
            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs("data/screenshots", exist_ok=True)
                save_path = f"data/screenshots/screenshot_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            gwen_logger.automation(f"Screenshot saved: {save_path}")
            return save_path
        except Exception as e:
            gwen_logger.error(f"Screenshot failed: {e}")
            return None
    
    # ─── COMMAND EXECUTION ──────────────────────────────────────────
    
    def run_command(self, command: str) -> Tuple[bool, str]:
        """Run a system command and return output."""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            output = result.stdout.strip() or result.stderr.strip()
            gwen_logger.automation(f"Command executed: {command[:50]}...")
            return True, output or "Command executed successfully sir!"
        except subprocess.TimeoutExpired:
            return False, "Command timed out sir."
        except Exception as e:
            gwen_logger.error(f"Command failed: {e}")
            return False, f"Command failed: {e}"
    
    def get_system_info(self) -> Dict[str, str]:
        """Get basic system information."""
        info = {
            "os": f"{platform.system()} {platform.release()}",
            "hostname": platform.node(),
            "python_version": sys.version.split()[0]
        }
        
        # Get CPU usage
        try:
            import psutil
            info["cpu"] = f"{psutil.cpu_percent()}%"
            info["memory"] = f"{psutil.virtual_memory().percent}%"
            info["uptime"] = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
        except ImportError:
            pass
        
        return info


# Global automation engine instance
automation = AutomationEngine()