import json
from pathlib import Path
from typing import Dict, Optional
from loguru import logger
from app.services.orchestrator import orchestrator

# In-memory session storage with file persistence
sessions = {}
SESSIONS_DIR = Path("data/sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def load_session(session_id: str) -> Optional[Dict]:
    """Get session from memory or load from disk."""
    # Always try loading from disk to ensure sync with Orchestrator
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if session_file.exists():
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
                sessions[session_id] = data
                return data
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    # Fallback to memory if file doesn't exist (unlikely if persisted correctly)
    if session_id in sessions:
        return sessions[session_id]

    return None

def save_session(session_id: str):
    """Save session to disk."""
    if session_id in sessions:
        try:
            session_file = SESSIONS_DIR / f"{session_id}.json"
            with open(session_file, "w") as f:
                # Use default=str to handle datetime objects
                json.dump(sessions[session_id], f, indent=2, default=str)

            # Invalidate orchestrator cache to ensure it reloads updated data
            if session_id in orchestrator.active_sessions:
                del orchestrator.active_sessions[session_id]

        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")

def get_session(session_id: str) -> Optional[Dict]:
    """Dependency wrapper for loading session"""
    return load_session(session_id)
