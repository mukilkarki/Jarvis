"""
logger.py - Logging system for Gwen AI
"""

import os
import logging
from datetime import datetime
from typing import Optional

# Color codes for terminal output
COLORS = {
    "RESET": "\033[0m",
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m"
}


class GwenLogger:
    """Custom logger with colored output for Gwen AI."""
    
    LEVEL_COLORS = {
        "DEBUG": COLORS["DIM"] + COLORS["WHITE"],
        "INFO": COLORS["GREEN"],
        "WARNING": COLORS["YELLOW"],
        "ERROR": COLORS["RED"],
        "CRITICAL": COLORS["RED"] + COLORS["BOLD"],
        "SYSTEM": COLORS["CYAN"] + COLORS["BOLD"],
        "AI": COLORS["MAGENTA"] + COLORS["BOLD"],
        "VOICE": COLORS["BLUE"] + COLORS["BOLD"],
        "MEMORY": COLORS["YELLOW"] + COLORS["BOLD"],
        "AUTO": COLORS["GREEN"] + COLORS["BOLD"]
    }
    
    def __init__(self, name: str = "GwenAI", log_dir: str = "data"):
        """Initialize logger."""
        self.name = name
        self.log_dir = log_dir
        self._setup_file_logging()
    
    def _setup_file_logging(self):
        """Setup file-based logging."""
        os.makedirs(self.log_dir, exist_ok=True)
        log_file = os.path.join(self.log_dir, f"gwen_{datetime.now().strftime('%Y%m%d')}.log")
        
        self.file_logger = logging.getLogger(self.name)
        self.file_logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
        fh.setFormatter(formatter)
        
        if not self.file_logger.handlers:
            self.file_logger.addHandler(fh)
    
    def _log(self, level: str, message: str, color_tag: Optional[str] = None):
        """Internal log method with colors."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = self.LEVEL_COLORS.get(level, COLORS["WHITE"])
        tag = f"[{color_tag or level}]" if color_tag else f"[{level}]"
        
        # Console output with colors
        print(f"{COLORS['DIM']}{timestamp}{COLORS['RESET']} {color}{tag}{COLORS['RESET']} {message}")
        
        # File output without colors
        if hasattr(self, 'file_logger'):
            log_method = getattr(self.file_logger, level.lower(), self.file_logger.info)
            log_method(f"{tag} {message}")
    
    def info(self, message: str, tag: str = "INFO"):
        """Log info message."""
        self._log("INFO", message, tag)
    
    def debug(self, message: str, tag: str = "DEBUG"):
        """Log debug message."""
        self._log("DEBUG", message, tag)
    
    def warning(self, message: str, tag: str = "WARNING"):
        """Log warning message."""
        self._log("WARNING", message, tag)
    
    def error(self, message: str, tag: str = "ERROR"):
        """Log error message."""
        self._log("ERROR", message, tag)
    
    def system(self, message: str):
        """Log system message."""
        self._log("SYSTEM", message, "SYSTEM")
    
    def ai(self, message: str):
        """Log AI interaction."""
        self._log("AI", message, "AI")
    
    def voice(self, message: str):
        """Log voice engine message."""
        self._log("VOICE", message, "VOICE")
    
    def memory(self, message: str):
        """Log memory operation."""
        self._log("MEMORY", message, "MEMORY")
    
    def automation(self, message: str):
        """Log automation command."""
        self._log("AUTO", message, "AUTO")


# Global logger instance
gwen_logger = GwenLogger()