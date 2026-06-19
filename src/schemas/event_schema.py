# src/schemas/event_schema.py

import re

# ISO-8601 or similar timestamp format validator (e.g. 2010-12-01 00:04:10)
TIMESTAMP_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$')

def validate_unified_event(event: dict) -> dict:
    """
    Validates a Unified Event dictionary against structural rules.
    If the event is valid, it returns the sanitized dictionary.
    Otherwise, raises ValueError.
    """
    required_fields = ["event_id", "timestamp", "user_id", "source", "event_type", "target", "details", "department", "role"]
    
    # 1. Check for required keys
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing mandatory Unified Event field: {field}")
            
    # 2. String check & strip values
    sanitized = {}
    for k, v in event.items():
        if v is None:
            sanitized[k] = "none"
        else:
            sanitized[k] = str(v).strip()
            
    # 3. Check format of timestamp
    if not TIMESTAMP_REGEX.match(sanitized["timestamp"]):
        raise ValueError(f"Invalid timestamp format: '{sanitized['timestamp']}'. Expected 'YYYY-MM-DD HH:MM:SS'.")

    # 4. Mandatory non-empty fields
    if not sanitized["event_id"] or sanitized["event_id"] == "none":
        raise ValueError("Unified Event field 'event_id' cannot be empty or 'none'.")
    if not sanitized["user_id"] or sanitized["user_id"] == "none":
        raise ValueError("Unified Event field 'user_id' cannot be empty or 'none'.")
    if not sanitized["source"] or sanitized["source"] == "none":
        raise ValueError("Unified Event field 'source' cannot be empty or 'none'.")
    if not sanitized["event_type"] or sanitized["event_type"] == "none":
        raise ValueError("Unified Event field 'event_type' cannot be empty or 'none'.")

    return sanitized


def validate_user_profile(user: dict) -> dict:
    """
    Validates user demographic metadata fields.
    Returns the sanitized user dictionary or raises ValueError.
    """
    required_fields = ["user_id", "name", "department", "role", "manager", "team"]
    
    for field in required_fields:
        if field not in user:
            raise ValueError(f"Missing mandatory User field: {field}")
            
    sanitized = {}
    for k, v in user.items():
        if v is None:
            sanitized[k] = "none"
        else:
            sanitized[k] = str(v).strip()
            
    if not sanitized["user_id"] or sanitized["user_id"] == "none":
        raise ValueError("User profile 'user_id' cannot be empty or 'none'.")
        
    return sanitized
