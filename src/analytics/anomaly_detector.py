# src/analytics/anomaly_detector.py

import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Ensure the parent 'src' directory is in PYTHONPATH for relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.database import get_connection, insert_anomaly_scores, DEFAULT_DB_PATH, initialize_database

# Exact 14 behavioral features approved in the blueprint
FEATURE_COLUMNS = [
    'logon_count', 'logoff_count', 'after_hours_logins', 'usb_insertions',
    'file_write_count', 'file_copy_to_usb', 'file_delete_count',
    'emails_sent', 'attachments_sent', 'email_exfil_bytes', 'unique_pcs',
    'total_events', 'first_activity_hour', 'last_activity_hour'
]

class AnomalyDetector:
    def __init__(self, model_path=None):
        if model_path is None:
            # Resolve model.pkl path relative to storage directory or package src folder
            model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model.pkl")
        self.model_path = model_path
        self.if_model = None
        self.lof_model = None
        self.lof_scaler = None
        self.if_score_scaler = None
        self.lof_score_scaler = None
        self.anomaly_threshold = 50.0  # Fallback threshold

    def train_on_profiles(self, df: pd.DataFrame):
        """
        Trains Isolation Forest (on raw numeric features) and Local Outlier Factor (on scaled numeric features).
        Calculates score normalization bounds and the 98th percentile anomaly threshold.
        """
        if df.empty:
            raise ValueError("Dataframe is empty. Cannot train model.")
            
        X_raw = df[FEATURE_COLUMNS].values
        
        # 1. Train Isolation Forest (scale-invariant, operates on raw features)
        self.if_model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42, n_jobs=-1)
        self.if_model.fit(X_raw)
        if_raw_scores = self.if_model.decision_function(X_raw)
        
        # 2. Preprocess and scale features strictly for distance-sensitive Local Outlier Factor
        self.lof_scaler = StandardScaler()
        X_scaled = self.lof_scaler.fit_transform(X_raw)
        
        # Train Local Outlier Factor
        self.lof_model = LocalOutlierFactor(n_neighbors=20, novelty=True, n_jobs=-1)
        self.lof_model.fit(X_scaled)
        lof_raw_scores = self.lof_model.score_samples(X_scaled)
        
        # 3. Fit score normalizers (MinMaxScaler). We invert the raw scores during 
        # fitting so that higher values (closer to 1.0) represent greater abnormality.
        self.if_score_scaler = MinMaxScaler(feature_range=(0, 1))
        if_norm = self.if_score_scaler.fit_transform((-if_raw_scores).reshape(-1, 1)).flatten()
        
        self.lof_score_scaler = MinMaxScaler(feature_range=(0, 1))
        lof_norm = self.lof_score_scaler.fit_transform((-lof_raw_scores).reshape(-1, 1)).flatten()
        
        # 4. Compute combined score (50% IF + 50% LOF) and map to 0-100 scale
        combined_norm_scores = 0.5 * if_norm + 0.5 * lof_norm
        combined_risk_scores = combined_norm_scores * 100.0
        
        # Set threshold at the 98th percentile to strictly enforce 2% outlier contamination
        self.anomaly_threshold = np.percentile(combined_risk_scores, 98)
        
        # 5. Serialize all trained instances to disk
        joblib.dump((
            self.if_model,
            self.lof_model,
            self.lof_scaler,
            self.if_score_scaler,
            self.lof_score_scaler,
            self.anomaly_threshold
        ), self.model_path)
        
        print(f"Models successfully trained and saved to: {self.model_path}")
        print(f"Ingested {len(df)} profiles. Calculated anomaly threshold (2% contamination): {self.anomaly_threshold:.4f}")

    def load_models(self):
        """Loads serialized model parameters."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}. Train the models first.")
        (
            self.if_model,
            self.lof_model,
            self.lof_scaler,
            self.if_score_scaler,
            self.lof_score_scaler,
            self.anomaly_threshold
        ) = joblib.load(self.model_path)

    def predict_profiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Loads models and scores the behavioral profiles.
        Returns a DataFrame matching the anomaly_scores schema:
        profile_id, if_score, lof_score, combined_score, is_anomaly
        """
        if (self.if_model is None or self.lof_model is None or
            self.lof_scaler is None or self.if_score_scaler is None or
            self.lof_score_scaler is None):
            self.load_models()
            
        X_raw = df[FEATURE_COLUMNS].values
        
        # 1. Isolation Forest scores
        if_raw = self.if_model.decision_function(X_raw)
        if_norm = self.if_score_scaler.transform((-if_raw).reshape(-1, 1)).flatten()
        if_norm = np.clip(if_norm, 0, 1)  # Bound checks
        
        # 2. Local Outlier Factor scores (StandardScaler applied beforehand)
        X_scaled = self.lof_scaler.transform(X_raw)
        lof_raw = self.lof_model.score_samples(X_scaled)
        lof_norm = self.lof_score_scaler.transform((-lof_raw).reshape(-1, 1)).flatten()
        lof_norm = np.clip(lof_norm, 0, 1)
        
        # 3. Combined score mapped to 0-100 range
        combined_norm = 0.5 * if_norm + 0.5 * lof_norm
        combined_risk = combined_norm * 100.0
        
        # 4. Check against the 98th percentile contamination boundary
        is_anomaly = (combined_risk >= self.anomaly_threshold).astype(int)
        
        results = pd.DataFrame({
            'profile_id': df['profile_id'],
            'if_score': if_norm * 100.0,
            'lof_score': lof_norm * 100.0,
            'combined_score': combined_risk,
            'is_anomaly': is_anomaly
        })
        return results

    # Compatibility wrappers for legacy / original interfaces
    def train(self, df: pd.DataFrame):
        """Wrapper aligning with baseline project schema."""
        self.train_on_profiles(df)

    def predict(self, df: pd.DataFrame) -> tuple:
        """Wrapper aligning with baseline prediction return signatures (risk_score, is_anomaly)."""
        results = self.predict_profiles(df)
        # Map 0/1 indicator back to the legacy -1/1 anomaly label format
        legacy_anomaly = results['is_anomaly'].map({1: -1, 0: 1})
        return (results['combined_score'], legacy_anomaly)


def run_analytics_pipeline(db_path: str = DEFAULT_DB_PATH):
    """Coordinates database profile loading, model training, risk scoring, and score updates."""
    print("=== Starting Analytics Ingestion Pipeline ===")
    
    # 1. Initialize database to ensure anomaly_scores table exists
    initialize_database(db_path)
    
    # 2. Load behavior profiles from SQLite
    conn = get_connection(db_path)
    df = pd.read_sql_query("SELECT * FROM behavior_profiles", conn)
    conn.close()
    
    if df.empty:
        raise ValueError("No behavioral profiles found in the database. Run feature engineering first.")
        
    # 2. Train models on existing profiles
    detector = AnomalyDetector()
    detector.train_on_profiles(df)
    
    # 3. Generate and store anomaly scores
    results = detector.predict_profiles(df)
    print(f"Writing {len(results)} anomaly scores to 'anomaly_scores' table...")
    insert_anomaly_scores(results, db_path)
    
    print("=== Analytics Pipeline Completed Successfully ===")


if __name__ == "__main__":
    # Resolve storage path relative to workspace setup
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(workspace_dir, "src", "storage", "shatrubodh.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}. Execute data collection and aggregation first.", file=sys.stderr)
        sys.exit(1)
        
    run_analytics_pipeline(db_path)
