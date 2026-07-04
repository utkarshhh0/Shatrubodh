# src/storage/database.py

import os
import sys
import sqlite3
import pandas as pd

# Ensure the parent 'src' directory is in PYTHONPATH for clean relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.ldap_collector import collect_users_chronologically, build_user_lookup
from collectors.cert_collector import (
    stream_logon_events,
    stream_device_events,
    stream_file_events,
    stream_email_events
)
from normalizers.event_normalizer import EventNormalizer

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shatrubodh.db")

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection with Foreign Keys, WAL, and safe sync settings."""
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    return conn


def initialize_database(db_path: str = DEFAULT_DB_PATH):
    """Creates the tables and indexes required by the approved blueprint."""
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        
        # 1. Create Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT NOT NULL,
                manager TEXT NOT NULL,
                team TEXT NOT NULL
            );
        """)
        
        # 2. Create Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                source TEXT NOT NULL,
                event_type TEXT NOT NULL,
                target TEXT NOT NULL,
                details TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
        """)
        
        # 3. Create Behavior Profiles Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_profiles (
                profile_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                profile_date TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT NOT NULL,
                logon_count INTEGER NOT NULL,
                logoff_count INTEGER NOT NULL,
                after_hours_logins INTEGER NOT NULL,
                usb_insertions INTEGER NOT NULL,
                file_write_count INTEGER NOT NULL,
                file_copy_to_usb INTEGER NOT NULL,
                file_delete_count INTEGER NOT NULL,
                emails_sent INTEGER NOT NULL,
                attachments_sent INTEGER NOT NULL,
                email_exfil_bytes INTEGER NOT NULL,
                unique_pcs INTEGER NOT NULL,
                total_events INTEGER NOT NULL,
                first_activity_hour REAL NOT NULL,
                last_activity_hour REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );
        """)
        
        # 4. Create Performance Optimizing Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_user_date ON behavior_profiles(user_id, profile_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_role_dept ON behavior_profiles(role, department);")
        
        # 5. Create Anomaly Scores Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anomaly_scores (
                profile_id TEXT PRIMARY KEY,
                if_score REAL NOT NULL,
                lof_score REAL NOT NULL,
                combined_score REAL NOT NULL,
                is_anomaly INTEGER NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES behavior_profiles(profile_id)
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scores_combined ON anomaly_scores(combined_score);")
        
        # 6. Create Risk Scores Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_scores (
                profile_id TEXT PRIMARY KEY,
                raw_anomaly_score REAL NOT NULL,
                context_multiplier REAL NOT NULL,
                risk_score REAL NOT NULL,
                risk_band TEXT NOT NULL,
                risk_reasons TEXT NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES behavior_profiles(profile_id)
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_scores_value ON risk_scores(risk_score);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_scores_band ON risk_scores(risk_band);")
        
        # 7. Create Alerts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                profile_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                alert_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'New',
                assigned_to TEXT,
                reasons TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                analyst_notes TEXT,
                FOREIGN KEY (profile_id) REFERENCES risk_scores(profile_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status_severity ON alerts(status, severity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_date ON alerts(user_id, alert_date);")
        
        conn.commit()
        print(f"Database initialized successfully at: {db_path}")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def insert_users(users: list, db_path: str = DEFAULT_DB_PATH):
    """
    Inserts a list of validated user profiles into the users table.
    Uses INSERT OR REPLACE to update context with historical/LDAP changes chronologically.
    """
    if not users:
        return
        
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR REPLACE INTO users (user_id, name, department, role, manager, team)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        user_tuples = [
            (u["user_id"], u["name"], u["department"], u["role"], u["manager"], u["team"])
            for u in users
        ]
        cursor.executemany(query, user_tuples)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def insert_events(events: list, db_path: str = DEFAULT_DB_PATH):
    """
    Inserts a list of normalized and validated Unified Events into the events table.
    Filters out 'department' and 'role' from the insert query as they belong strictly
    to the users table.
    """
    if not events:
        return
        
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO events (event_id, timestamp, user_id, source, event_type, target, details)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        event_tuples = []
        for ev in events:
            eid = ev.get("event_id") or ev.get("id")
            if not eid:
                raise ValueError("Event does not contain a unique event_id / id.")
                
            event_tuples.append((
                eid,
                ev["timestamp"],
                ev["user_id"],
                ev["source"],
                ev["event_type"],
                ev["target"],
                ev["details"]
            ))
        cursor.executemany(query, event_tuples)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def insert_behavior_profiles(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH):
    """
    Bulk inserts behavioral profiles into the behavior_profiles table.
    Uses INSERT OR REPLACE to update stats during re-runs.
    """
    if df.empty:
        return
        
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR REPLACE INTO behavior_profiles (
                profile_id, user_id, profile_date, department, role,
                logon_count, logoff_count, after_hours_logins, usb_insertions,
                file_write_count, file_copy_to_usb, file_delete_count,
                emails_sent, attachments_sent, email_exfil_bytes, unique_pcs, total_events,
                first_activity_hour, last_activity_hour
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        tuples = list(df.itertuples(index=False, name=None))
        cursor.executemany(query, tuples)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def insert_anomaly_scores(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH):
    """
    Bulk inserts combined anomaly scores into the anomaly_scores table.
    Uses INSERT OR REPLACE to update stats during re-runs.
    """
    if df.empty:
        return
        
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR REPLACE INTO anomaly_scores (
                profile_id, if_score, lof_score, combined_score, is_anomaly
            ) VALUES (?, ?, ?, ?, ?);
        """
        tuples = list(df[['profile_id', 'if_score', 'lof_score', 'combined_score', 'is_anomaly']].itertuples(index=False, name=None))
        cursor.executemany(query, tuples)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def insert_risk_scores(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH):
    """
    Bulk inserts combined risk scores into the risk_scores table.
    Uses INSERT OR REPLACE to update stats during re-runs.
    """
    if df.empty:
        return
        
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR REPLACE INTO risk_scores (
                profile_id, raw_anomaly_score, context_multiplier, risk_score, risk_band, risk_reasons
            ) VALUES (?, ?, ?, ?, ?, ?);
        """
        tuples = list(df[['profile_id', 'raw_anomaly_score', 'context_multiplier', 'risk_score', 'risk_band', 'risk_reasons']].itertuples(index=False, name=None))
        cursor.executemany(query, tuples)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def insert_alerts(df: pd.DataFrame, db_path: str = DEFAULT_DB_PATH):
    """
    Bulk inserts alerts into the alerts table.
    Uses INSERT OR IGNORE since duplicate prevention is key (UNIQUE profile_id constraint).
    """
    if df.empty:
        return
        
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO alerts (
                alert_id, profile_id, user_id, alert_date, created_at,
                severity, status, assigned_to, reasons, evidence_json, analyst_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        tuples = list(df[[
            'alert_id', 'profile_id', 'user_id', 'alert_date', 'created_at',
            'severity', 'status', 'assigned_to', 'reasons', 'evidence_json', 'analyst_notes'
        ]].itertuples(index=False, name=None))
        cursor.executemany(query, tuples)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()


def run_full_ingestion_pipeline(dataset_dir: str, db_path: str = DEFAULT_DB_PATH):
    """Coordinates tables setup, user demographics context loading, and chunked events parsing."""
    print(f"=== Starting Ingestion Pipeline (Database: {db_path}) ===")
    
    # 1. Setup tables and index
    initialize_database(db_path)
    
    # 2. Extract and load LDAP demographics context
    print("Ingesting User Context and LDAP Snapshots...")
    users_dict = collect_users_chronologically(dataset_dir)
    print(f"Parsed {len(users_dict)} unique historical user profiles.")
    
    user_list = list(users_dict.values())
    insert_users(user_list, db_path)
    print("User demographic records stored successfully.")
    
    # 3. Create normalization translator with cached context lookups
    lookup = build_user_lookup(users_dict)
    normalizer = EventNormalizer(lookup)
    
    # 4. Ingest Logon Logs
    print("Ingesting Logon events...")
    logon_count = 0
    for chunk in stream_logon_events(dataset_dir):
        normalized_chunk = [normalizer.normalize_logon(raw) for raw in chunk]
        insert_events(normalized_chunk, db_path)
        logon_count += len(normalized_chunk)
        print(f"  Inserted {logon_count} Logon events...")
    print(f"Total Logon events: {logon_count}")
    
    # 5. Ingest Device Logs
    print("Ingesting Device events...")
    device_count = 0
    for chunk in stream_device_events(dataset_dir):
        normalized_chunk = [normalizer.normalize_device(raw) for raw in chunk]
        insert_events(normalized_chunk, db_path)
        device_count += len(normalized_chunk)
        print(f"  Inserted {device_count} Device events...")
    print(f"Total Device events: {device_count}")
    
    # 6. Ingest File Logs
    print("Ingesting File events...")
    file_count = 0
    for chunk in stream_file_events(dataset_dir):
        normalized_chunk = [normalizer.normalize_file(raw) for raw in chunk]
        insert_events(normalized_chunk, db_path)
        file_count += len(normalized_chunk)
        print(f"  Inserted {file_count} File events...")
    print(f"Total File events: {file_count}")
    
    # 7. Ingest Email Logs
    print("Ingesting Email events...")
    email_count = 0
    for chunk in stream_email_events(dataset_dir):
        normalized_chunk = [normalizer.normalize_email(raw) for raw in chunk]
        insert_events(normalized_chunk, db_path)
        email_count += len(normalized_chunk)
        print(f"  Inserted {email_count} Email events...")
    print(f"Total Email events: {email_count}")
    
    print("=== Ingestion Pipeline Completed Successfully ===")


if __name__ == "__main__":
    # Resolve the default dataset folder location in relation to workspace layout
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dataset_dir = os.path.join(workspace_dir, "src", "dataset")
    
    if not os.path.exists(dataset_dir):
        print(f"Error: Authoritative dataset directory not found at {dataset_dir}", file=sys.stderr)
        sys.exit(1)
        
    run_full_ingestion_pipeline(dataset_dir)
