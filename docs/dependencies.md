# Shatrubodh Dependencies

This document outlines the dependencies required to run the Shatrubodh SOC Dashboard, behavior profile analysis, and anomaly detection pipelines.

## streamlit
- **Version**: 1.51.0
- **Install**: `pip install streamlit==1.51.0`
- **Purpose**: Provides the operational SOC Dashboard user interface, pages, charts, caching utilities, and analyst triage interactions.
- **Used In**:
  - `src/app.py`
  - `src/dashboard/components/charts.py`
  - `src/dashboard/pages/alert_queue.py`
  - `src/dashboard/pages/reports.py`
  - `src/dashboard/pages/threat_hunter.py`
  - `src/dashboard/services/db_service.py`

## pandas
- **Version**: 2.3.3
- **Install**: `pip install pandas==2.3.3`
- **Purpose**: Used for database query ingestion, dataframe slicing, data conversions, statistical baseline computations, and rendering UI tables.
- **Used In**:
  - `src/analytics/alert_generator.py`
  - `src/analytics/anomaly_detector.py`
  - `src/analytics/risk_engine.py`
  - `src/dashboard/components/charts.py`
  - `src/dashboard/pages/alert_queue.py`
  - `src/dashboard/pages/reports.py`
  - `src/dashboard/pages/threat_hunter.py`
  - `src/dashboard/services/db_service.py`
  - `src/dashboard/services/evidence_parser.py`
  - `src/feature_engineering/behavior_profiles.py`

## numpy
- **Version**: 2.3.1
- **Install**: `pip install numpy==2.3.1`
- **Purpose**: Vectorized mathematical arrays handling, anomaly threshold percentile estimation, and risk band classification criteria.
- **Used In**:
  - `src/analytics/alert_generator.py`
  - `src/analytics/anomaly_detector.py`
  - `src/analytics/risk_engine.py`
  - `src/dashboard/services/evidence_parser.py`

## scikit-learn
- **Version**: 1.7.2
- **Install**: `pip install scikit-learn==1.7.2`
- **Purpose**: Evaluates user activity via machine learning models (IsolationForest and LocalOutlierFactor) to identify behavior profile anomalies.
- **Used In**:
  - `src/analytics/anomaly_detector.py`

## joblib
- **Version**: 1.5.2
- **Install**: `pip install joblib==1.5.2`
- **Purpose**: Serializes and deserializes the trained estimators, scalers, and dynamic anomaly thresholds.
- **Used In**:
  - `src/analytics/anomaly_detector.py`

***

## Installation Command

To install all dependencies with pinned production versions in one command, run:

```bash
pip install streamlit==1.51.0 pandas==2.3.3 numpy==2.3.1 scikit-learn==1.7.2 joblib==1.5.2
```
