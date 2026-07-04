# src/analytics/alert_generator.py

import os
import sys
import pandas as pd
import numpy as np
import uuid
import datetime
import json

# Ensure the parent 'src' directory is in PYTHONPATH for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import get_connection, insert_alerts, DEFAULT_DB_PATH, initialize_database

class AlertGenerator:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path

    def generate_new_alerts(self) -> pd.DataFrame:
        """
        Queries risk scores that have a risk_score >= 50.0 and do not have an existing alert.
        Constructs the alert records with complete behavioral profile JSON evidence.
        """
        conn = get_connection(self.db_path)
        try:
            # Pull risk scores and behavior profiles that are not yet alerted
            query = """
                SELECT 
                    r.profile_id, 
                    r.risk_score, 
                    r.risk_reasons as reasons,
                    b.user_id,
                    b.profile_date as alert_date,
                    b.profile_date,
                    b.department,
                    b.role,
                    b.logon_count,
                    b.logoff_count,
                    b.after_hours_logins,
                    b.usb_insertions,
                    b.file_write_count,
                    b.file_copy_to_usb,
                    b.file_delete_count,
                    b.emails_sent,
                    b.attachments_sent,
                    b.email_exfil_bytes,
                    b.unique_pcs,
                    b.total_events,
                    b.first_activity_hour,
                    b.last_activity_hour
                FROM risk_scores r
                JOIN behavior_profiles b ON r.profile_id = b.profile_id
                LEFT JOIN alerts a ON r.profile_id = a.profile_id
                WHERE r.risk_score >= 50.0 AND a.profile_id IS NULL
            """
            df = pd.read_sql_query(query, conn)
        finally:
            conn.close()
        
        if df.empty:
            print("No new risk profiles qualify for alert generation (risk_score >= 50.0 and not already alerted).")
            return pd.DataFrame()

        # Generate alert details
        df['alert_id'] = [f"alt_{uuid.uuid4().hex[:12]}" for _ in range(len(df))]
        
        created_at_val = datetime.datetime.now(datetime.timezone.utc).isoformat()
        df['created_at'] = created_at_val
        
        df['status'] = 'New'
        df['assigned_to'] = None
        df['analyst_notes'] = None
        
        # Severity mapping:
        # 50.0 <= risk_score < 70.0 -> Medium
        # 70.0 <= risk_score < 85.0 -> High
        # risk_score >= 85.0 -> Critical
        conditions = [
            df['risk_score'] < 70.0,
            (df['risk_score'] >= 70.0) & (df['risk_score'] < 85.0),
            df['risk_score'] >= 85.0
        ]
        choices = ['Medium', 'High', 'Critical']
        df['severity'] = np.select(conditions, choices, default='Medium')
        
        # Serialize full behavior profile details into evidence_json
        cols_to_serialize = [
            'profile_id', 'user_id', 'profile_date', 'department', 'role',
            'logon_count', 'logoff_count', 'after_hours_logins', 'usb_insertions',
            'file_write_count', 'file_copy_to_usb', 'file_delete_count',
            'emails_sent', 'attachments_sent', 'email_exfil_bytes', 'unique_pcs',
            'total_events', 'first_activity_hour', 'last_activity_hour'
        ]
        df['evidence_json'] = df[cols_to_serialize].apply(lambda r: json.dumps(r.to_dict()), axis=1)
        
        # Validation checks on generated alerts
        if not (df['alert_id'].str.match(r'^alt_[a-f0-9]{12}$') & (df['alert_id'].notnull())).all():
            raise ValueError("alert_id must match alt_<12-hex>")
        if not set(df['severity'].unique()).issubset({'Medium', 'High', 'Critical'}):
            raise ValueError("severity must be Medium, High, or Critical")
        if not set(df['status'].unique()).issubset({'New', 'In_Progress', 'Resolved', 'False_Positive'}):
            raise ValueError("status must be valid")
        if not df['profile_id'].notnull().all():
            raise ValueError("profile_id cannot be null")
        if not (df['user_id'].notnull() & (df['user_id'] != '')).all():
            raise ValueError("user_id cannot be null or empty")

        # Return fields aligned with the alerts table schema
        return df[[
            'alert_id', 'profile_id', 'user_id', 'alert_date', 'created_at',
            'severity', 'status', 'assigned_to', 'reasons', 'evidence_json', 'analyst_notes'
        ]]


def run_alerts_pipeline(db_path: str = DEFAULT_DB_PATH):
    """Executes database schema synchronization and generates alerts from new risk scores."""
    print("=== Starting Alert Generation Pipeline ===")
    
    # 1. Initialize schema to ensure alerts table and indexes exist
    initialize_database(db_path)
    
    # 2. Compute/generate alert records
    generator = AlertGenerator(db_path)
    new_alerts_df = generator.generate_new_alerts()
    
    if new_alerts_df.empty:
        print("=== Alert Generation Pipeline Completed (0 alerts added) ===")
        return
        
    print(f"Generated {len(new_alerts_df)} new alerts.")
    
    # 3. Store alerts in SQLite
    print("Writing alerts to database...")
    insert_alerts(new_alerts_df, db_path)
    
    print("=== Alert Generation Pipeline Completed Successfully ===")


if __name__ == "__main__":
    # Resolve storage path relative to workspace setup
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(workspace_dir, "src", "storage", "shatrubodh.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}.", file=sys.stderr)
        sys.exit(1)
        
    run_alerts_pipeline(db_path)
