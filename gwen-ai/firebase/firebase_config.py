"""
firebase_config.py - Firebase configuration for Gwen AI
"""

import os
import json
from typing import Optional

from utils.logger import gwen_logger

# Firebase configuration
FIREBASE_CONFIG = {
    "type": os.getenv("FIREBASE_TYPE", "service_account"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
    "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER", "https://www.googleapis.com/oauth2/v1/certs"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL", "")
}

# Collection names
COLLECTIONS = {
    "memories": "gwen_memories",
    "productivity": "gwen_productivity",
    "reminders": "gwen_reminders",
    "settings": "gwen_settings",
    "conversations": "gwen_conversations",
    "emotions": "gwen_emotions",
    "stats": "gwen_stats"
}

# Subcollection names
SUBCOLLECTIONS = {
    "daily_quests": "daily_quests",
    "achievements": "achievements",
    "habit_tracker": "habit_tracker",
    "focus_sessions": "focus_sessions"
}


def validate_firebase_config() -> bool:
    """Validate that Firebase configuration is complete."""
    required_fields = ["project_id", "private_key", "client_email"]
    
    for field in required_fields:
        if not FIREBASE_CONFIG.get(field):
            gwen_logger.warning(f"Firebase config missing: {field}")
            return False
    
    gwen_logger.system("Firebase configuration validated")
    return True


def get_firebase_credential_path() -> Optional[str]:
    """
    Get or create Firebase credential file.
    Returns path to credential file or None.
    """
    cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH", "")
    
    if cred_path and os.path.exists(cred_path):
        return cred_path
    
    # Try to create from environment variables
    if validate_firebase_config():
        try:
            cred_dir = "data"
            os.makedirs(cred_dir, exist_ok=True)
            cred_path = os.path.join(cred_dir, "firebase_credentials.json")
            
            with open(cred_path, "w") as f:
                json.dump(FIREBASE_CONFIG, f, indent=2)
            
            gwen_logger.system(f"Firebase credentials saved to {cred_path}")
            return cred_path
        except Exception as e:
            gwen_logger.error(f"Failed to save Firebase credentials: {e}")
    
    return None


# .env file loader
def load_env_file(env_path: str = ".env"):
    """Load environment variables from .env file."""
    try:
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
            gwen_logger.system(f"Loaded environment from {env_path}")
            return True
    except Exception as e:
        gwen_logger.error(f"Failed to load .env: {e}")
    
    return False