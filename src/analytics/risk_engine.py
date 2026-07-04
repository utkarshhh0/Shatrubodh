# src/analytics/risk_engine.py

import os
import sys
import pandas as pd
import numpy as np

# Ensure the parent 'src' directory is in PYTHONPATH for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import get_connection, insert_risk_scores, DEFAULT_DB_PATH, initialize_database

class RiskEngine:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path

    def compute_risk_profiles(self) -> pd.DataFrame:
        """
        Loads anomaly scores and behavior profiles, applies headroom-scaled multipliers,
        computes the final risk scores, assigns risk bands, and generates explanations.
        """
        conn = get_connection(self.db_path)
        try:
            # Load unified features and anomaly scores
            query = """
                SELECT 
                    a.profile_id, 
                    a.combined_score as raw_anomaly_score, 
                    a.is_anomaly,
                    b.file_copy_to_usb,
                    b.email_exfil_bytes,
                    b.after_hours_logins
                FROM anomaly_scores a
                JOIN behavior_profiles b ON a.profile_id = b.profile_id
            """
            df = pd.read_sql_query(query, conn)
        finally:
            conn.close()
        
        if df.empty:
            raise ValueError("No anomaly scores found in the database. Run anomaly detector first.")

        required_cols = ['profile_id', 'raw_anomaly_score', 'is_anomaly', 'file_copy_to_usb', 'email_exfil_bytes', 'after_hours_logins']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Loaded dataframe is missing columns: {missing_cols}")

        # Vectorized calculations of scaled multipliers
        # f(usb) = min(file_copy_to_usb / 5.0, 1.0)
        f_usb = np.minimum(df['file_copy_to_usb'] / 5.0, 1.0)
        
        # f(exfil) = min(email_exfil_bytes / 50000000.0, 1.0)
        f_exfil = np.minimum(df['email_exfil_bytes'] / 50000000.0, 1.0)
        
        # f(hours) = min(after_hours_logins / 3.0, 1.0)
        f_hours = np.minimum(df['after_hours_logins'] / 3.0, 1.0)
        
        # M = 1.0 + is_anomaly * (0.40 * f_usb + 0.35 * f_exfil + 0.25 * f_hours)
        multiplier_contribution = 0.40 * f_usb + 0.35 * f_exfil + 0.25 * f_hours
        df['context_multiplier'] = 1.0 + np.where(df['is_anomaly'] == 1, multiplier_contribution, 0.0)
        
        # RiskScore = RawAnomalyScore + (100.0 - RawAnomalyScore) * (M - 1.0)
        df['risk_score'] = df['raw_anomaly_score'] + (100.0 - df['raw_anomaly_score']) * (df['context_multiplier'] - 1.0)
        
        # Vectorized Risk Banding
        conditions = [
            df['risk_score'] < 25.0,
            (df['risk_score'] >= 25.0) & (df['risk_score'] < 50.0),
            (df['risk_score'] >= 50.0) & (df['risk_score'] < 75.0),
            df['risk_score'] >= 75.0
        ]
        choices = ['Low', 'Medium', 'High', 'Critical']
        df['risk_band'] = np.select(conditions, choices, default='Low')
        
        # Validation checks:
        if not df['context_multiplier'].between(1.0, 2.0).all():
            raise ValueError("context_multiplier must lie in [1.0, 2.0]")
        if not df['risk_score'].between(0.0, 100.0).all():
            raise ValueError("risk_score must lie in [0.0, 100.0]")
        if not set(df['risk_band'].unique()).issubset({'Low', 'Medium', 'High', 'Critical'}):
            raise ValueError("risk_band must contain values in Low, Medium, High, Critical")

        # Generate human-readable reasons row-by-row for rich strings
        def generate_reasons(row):
            reasons = []
            if row['is_anomaly'] == 1:
                reasons.append(f"Anomaly detected (Score: {row['raw_anomaly_score']:.1f})")
            if row['file_copy_to_usb'] > 0:
                reasons.append(f"USB copy ({int(row['file_copy_to_usb'])} files)")
            if row['email_exfil_bytes'] > 0:
                size_mb = row['email_exfil_bytes'] / (1024 * 1024)
                reasons.append(f"Email exfil ({size_mb:.2f} MB)")
            if row['after_hours_logins'] > 0:
                reasons.append(f"Late logins ({int(row['after_hours_logins'])} events)")
            
            if not reasons:
                return "Baseline compliance"
            return ", ".join(reasons)
            
        df['risk_reasons'] = df.apply(generate_reasons, axis=1)
        
        return df[['profile_id', 'raw_anomaly_score', 'context_multiplier', 'risk_score', 'risk_band', 'risk_reasons']]


def run_risk_pipeline(db_path: str = DEFAULT_DB_PATH):
    """Runs the risk engine scoring and saves results to SQLite."""
    print("=== Starting Risk Engine Pipeline ===")
    
    # Ensure database initialize has run (which now creates risk_scores table and indexes)
    initialize_database(db_path)
    
    engine = RiskEngine(db_path)
    risk_df = engine.compute_risk_profiles()
    
    print(f"Computed {len(risk_df)} risk profiles.")
    
    # Store results in SQLite
    print("Writing risk profiles to SQLite...")
    insert_risk_scores(risk_df, db_path)
    
    print("=== Risk Engine Pipeline Completed Successfully ===")


if __name__ == "__main__":
    # Resolve storage path relative to workspace setup
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(workspace_dir, "src", "storage", "shatrubodh.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}.", file=sys.stderr)
        sys.exit(1)
        
    run_risk_pipeline(db_path)
