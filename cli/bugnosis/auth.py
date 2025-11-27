"""Secure authentication management."""

import keyring
import sys
import getpass
from typing import Optional

SERVICE_NAME = "bugnosis"

def set_token(platform: str, token: str):
    """Securely store an API token."""
    try:
        keyring.set_password(SERVICE_NAME, platform, token)
    except Exception as e:
        print(f"Warning: Could not use system keyring: {e}")
        # Fallback or error handling - for now just warn
        
def get_token(platform: str) -> Optional[str]:
    """Retrieve a stored API token."""
    try:
        return keyring.get_password(SERVICE_NAME, platform)
    except Exception:
        return None

def delete_token(platform: str):
    """Remove a stored API token."""
    try:
        keyring.delete_password(SERVICE_NAME, platform)
    except Exception:
        pass

