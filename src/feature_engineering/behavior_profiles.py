# src/feature_engineering/behavior_profiles.py

import os
import sys
import pandas as pd

# Ensure parent 'src' directory is in PYTHONPATH for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import get_connection, insert_behavior_profiles, DEFAULT_DB_PATH


def extract_email_size(details: str) -> int:
    """Extracts size integer from the email details string 'Size: 25363 | CC: ...'"""
    if not details or not details.startswith("Size: "):
        return 0
    try:
        parts = details.split(" | ", 1)
        size_str = parts[0].split(": ")[1]
        return int(size_str)
    except Exception:
        return 0


def has_attachments(details: str) -> int:
    """Returns 1 if the email has one or more attachments, 0 otherwise."""
    if not details:
        return 0
    try:
        # Search for attachments section
        idx = details.find("Attachments: ")
        if idx == -1:
            return 0
        end_idx = details.find(" | ", idx)
        if end_idx == -1:
            attachments_part = details[idx + 13:]
        else:
            attachments_part = details[idx + 13:end_idx]
            
        attachments_part = attachments_part.strip()
        if attachments_part == "none" or not attachments_part:
            return 0
        return 1
    except Exception:
        return 0


def time_to_hours(timestamp_str: str) -> float:
    """Converts time component of 'YYYY-MM-DD HH:MM:SS' string to a float decimal hour."""
    if not timestamp_str or len(timestamp_str) < 19:
        return 0.0
    try:
        time_part = timestamp_str.split(" ")[1]
        h, m, s = time_part.split(":")
        return int(h) + int(m) / 60.0 + int(s) / 3600.0
    except Exception:
        return 0.0


def generate_user_day_profiles(db_path: str = DEFAULT_DB_PATH, chunk_size: int = 50000):
    """
    Runs the SQLite aggregation query, streams result chunks,
    and commits them to the behavior_profiles table.
    """
    print(f"Aggregating behavioral events from database to build User-Day profiles...")
    conn = get_connection(db_path)
    try:
        # Register custom scalar functions in SQLite
        conn.create_function("EXTRACT_EMAIL_SIZE", 1, extract_email_size)
        conn.create_function("HAS_ATTACHMENTS", 1, has_attachments)
        conn.create_function("TIME_TO_HOURS", 1, time_to_hours)
        
        # Aggregation Query in SQLite mapping exactly to the approved table schema
        query = """
            SELECT
                (e.user_id || '_' || date(e.timestamp)) AS profile_id,
                e.user_id,
                date(e.timestamp) AS profile_date,
                u.department,
                u.role,
                COUNT(CASE WHEN e.event_type = 'Logon' THEN 1 END) AS logon_count,
                COUNT(CASE WHEN e.event_type = 'Logoff' THEN 1 END) AS logoff_count,
                COUNT(CASE WHEN e.event_type = 'Logon' AND (time(e.timestamp) >= '18:00:00' OR time(e.timestamp) <= '06:00:00') THEN 1 END) AS after_hours_logins,
                COUNT(CASE WHEN e.event_type = 'Connect' THEN 1 END) AS usb_insertions,
                COUNT(CASE WHEN e.event_type = 'File Write' THEN 1 END) AS file_write_count,
                COUNT(CASE WHEN e.event_type = 'File Copy' AND e.details LIKE '%To USB: True%' THEN 1 END) AS file_copy_to_usb,
                COUNT(CASE WHEN e.event_type = 'File Delete' THEN 1 END) AS file_delete_count,
                COUNT(CASE WHEN e.event_type = 'Send' THEN 1 END) AS emails_sent,
                SUM(CASE WHEN e.event_type = 'Send' THEN HAS_ATTACHMENTS(e.details) ELSE 0 END) AS attachments_sent,
                SUM(CASE WHEN e.event_type = 'Send' THEN EXTRACT_EMAIL_SIZE(e.details) ELSE 0 END) AS email_exfil_bytes,
                COUNT(DISTINCT e.source) AS unique_pcs,
                COUNT(e.event_id) AS total_events,
                MIN(TIME_TO_HOURS(e.timestamp)) AS first_activity_hour,
                MAX(TIME_TO_HOURS(e.timestamp)) AS last_activity_hour
            FROM events e
            LEFT JOIN users u ON e.user_id = u.user_id
            GROUP BY e.user_id, profile_date;
        """
        
        total_inserted = 0
        # Stream query result chunks to keep memory consumption low
        for chunk in pd.read_sql_query(query, conn, chunksize=chunk_size):
            # Fill missing values and ensure correct types
            chunk['attachments_sent'] = chunk['attachments_sent'].fillna(0).astype(int)
            chunk['email_exfil_bytes'] = chunk['email_exfil_bytes'].fillna(0).astype(int)
            
            insert_behavior_profiles(chunk, db_path)
            total_inserted += len(chunk)
            print(f"  Processed and committed {total_inserted} profiles...")
            
        print(f"Successfully generated and stored {total_inserted} User-Day profiles in SQLite database.")
    finally:
        conn.close()


if __name__ == "__main__":
    if not os.path.exists(DEFAULT_DB_PATH):
        print(f"Error: Database not found at {DEFAULT_DB_PATH}. Run the raw database ingestion first.", file=sys.stderr)
        sys.exit(1)
        
    generate_user_day_profiles()
