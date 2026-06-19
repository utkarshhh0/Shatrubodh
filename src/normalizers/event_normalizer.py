# src/normalizers/event_normalizer.py

import sys
import os

# Safeguard imports when running script directly or as part of a package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas.event_schema import validate_unified_event

class EventNormalizer:
    def __init__(self, user_lookup: dict):
        """
        Initializes the normalizer with a preloaded user demographic lookup dictionary.
        user_lookup: dictionary of user_id -> { "department": str, "role": str }
        """
        self.user_lookup = user_lookup

    def _enrich_user_context(self, event_dict: dict, user_id: str):
        """Helper to inject department and role from lookup dictionary."""
        user_info = self.user_lookup.get(user_id, {})
        event_dict["department"] = user_info.get("department", "none")
        event_dict["role"] = user_info.get("role", "none")

    def normalize_logon(self, raw: dict) -> dict:
        """
        Maps raw Logon row to Unified Event.
        Raw fields: id, date, user, pc, activity
        """
        user_id = str(raw.get("user", "none")).strip()
        unified = {
            "event_id": str(raw.get("id", "none")).strip(),
            "timestamp": str(raw.get("date", "none")).strip(),
            "user_id": user_id,
            "source": str(raw.get("pc", "none")).strip(),
            "event_type": str(raw.get("activity", "none")).strip(),
            "target": str(raw.get("pc", "none")).strip(),
            "details": f"Activity: {raw.get('activity', 'none')}"
        }
        self._enrich_user_context(unified, user_id)
        return validate_unified_event(unified)

    def normalize_device(self, raw: dict) -> dict:
        """
        Maps raw Device row to Unified Event.
        Raw fields: id, date, user, pc, file_tree, activity
        """
        user_id = str(raw.get("user", "none")).strip()
        unified = {
            "event_id": str(raw.get("id", "none")).strip(),
            "timestamp": str(raw.get("date", "none")).strip(),
            "user_id": user_id,
            "source": str(raw.get("pc", "none")).strip(),
            "event_type": str(raw.get("activity", "none")).strip(),
            "target": str(raw.get("file_tree", "none")).strip(),
            "details": f"Activity: {raw.get('activity', 'none')} | File Tree: {raw.get('file_tree', 'none')}"
        }
        self._enrich_user_context(unified, user_id)
        return validate_unified_event(unified)

    def normalize_file(self, raw: dict) -> dict:
        """
        Maps raw File row to Unified Event.
        Raw fields: id, date, user, pc, filename, activity, to_removable_media, from_removable_media, content
        """
        user_id = str(raw.get("user", "none")).strip()
        
        # Detail extraction
        to_removable = str(raw.get("to_removable_media", "False")).strip()
        from_removable = str(raw.get("from_removable_media", "False")).strip()
        content_snippet = str(raw.get("content", ""))[:200].strip() # Limit string snippet
        
        unified = {
            "event_id": str(raw.get("id", "none")).strip(),
            "timestamp": str(raw.get("date", "none")).strip(),
            "user_id": user_id,
            "source": str(raw.get("pc", "none")).strip(),
            "event_type": str(raw.get("activity", "none")).strip(),
            "target": str(raw.get("filename", "none")).strip(),
            "details": f"Activity: {raw.get('activity', 'none')} | To USB: {to_removable} | From USB: {from_removable} | Content: {content_snippet}"
        }
        self._enrich_user_context(unified, user_id)
        return validate_unified_event(unified)

    def normalize_email(self, raw: dict) -> dict:
        """
        Maps raw Email row to Unified Event.
        Raw fields: id, date, user, pc, to, cc, bcc, from, activity, size, attachments, content
        """
        user_id = str(raw.get("user", "none")).strip()
        
        # Details aggregation
        size = str(raw.get("size", "0")).strip()
        cc = str(raw.get("cc", "")).strip()
        bcc = str(raw.get("bcc", "")).strip()
        attachments = str(raw.get("attachments", "")).strip()
        content_snippet = str(raw.get("content", ""))[:200].strip()
        
        unified = {
            "event_id": str(raw.get("id", "none")).strip(),
            "timestamp": str(raw.get("date", "none")).strip(),
            "user_id": user_id,
            "source": str(raw.get("pc", "none")).strip(),
            "event_type": str(raw.get("activity", "none")).strip(),
            "target": str(raw.get("to", "none")).strip(),
            "details": f"Size: {size} | CC: {cc} | BCC: {bcc} | Attachments: {attachments} | Content: {content_snippet}"
        }
        self._enrich_user_context(unified, user_id)
        return validate_unified_event(unified)

    def normalize_event(self, raw: dict, category: str) -> dict:
        """Helper router to dispatch raw rows based on source categories."""
        if category == "logon":
            return self.normalize_logon(raw)
        elif category == "device":
            return self.normalize_device(raw)
        elif category == "file":
            return self.normalize_file(raw)
        elif category == "email":
            return self.normalize_email(raw)
        else:
            raise ValueError(f"Unknown event category: {category}")
