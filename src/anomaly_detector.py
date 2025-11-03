
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
from src.utils import create_preprocessor, prepare_data_for_model

class AnomalyDetector:
    def __init__(self, model_path="src/model.pkl"):
        self.model_path = model_path
        self.model = None
        self.preprocessor = None

    def train(self, df):
        self.preprocessor = create_preprocessor()
        df_prepared = prepare_data_for_model(df)
        processed_data = self.preprocessor.fit_transform(df_prepared)
        self.model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
        self.model.fit(processed_data)
        joblib.dump((self.model, self.preprocessor), self.model_path)

    def predict(self, df):
        if self.model is None or self.preprocessor is None:
            try: self.model, self.preprocessor = joblib.load(self.model_path)
            except FileNotFoundError: raise FileNotFoundError("Model not found. Please train the model first.")

        df_prepared = prepare_data_for_model(df)
        processed_data = self.preprocessor.transform(df_prepared)
        anomaly_scores = self.model.decision_function(processed_data)
        
        scaler = MinMaxScaler(feature_range=(0, 1))
        risk_scores = scaler.fit_transform(anomaly_scores.reshape(-1, 1))
        risk_scores = (1 - risk_scores) * 100
        
        is_anomaly = self.model.predict(processed_data)
        
        # Return only the results, not a modified DataFrame
        return pd.Series(risk_scores.flatten(), name='risk_score', index=df.index), pd.Series(is_anomaly, name='is_anomaly', index=df.index)
