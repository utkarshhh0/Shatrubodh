Date/Time: 2026-06-19 20:10 (IST)
Files Modified: None (Created: src/schemas/event_schema.py, src/storage/database.py, src/normalizers/event_normalizer.py, src/collectors/ldap_collector.py, src/collectors/cert_collector.py)
Reason: Implement Phase 1 blueprint (Data Collection, Normalization, and SQLite Storage) in alignment with DRDO Modules 1 and 2.
Changes Implemented:
  - Created validation schemas for user profiles and Unified Events.
  - Implemented memory-safe, generator-based CERT activity log collectors using Pandas chunking.
  - Implemented chronological LDAP context collection and lookup dictionary builders.
  - Designed the event normalizer with direct lookup-map context injection and schema validation.
  - Developed database initialization, table/index definitions, and transactional bulk insertion hooks directly in database.py.
Dependencies Added: None (Standard: pandas, sqlite3, os, glob)
Known Issues: None (Tested baseline collectors locally with successful output)
Next Recommended Step: Connect the Streamlit UI (app.py) and anomaly detector (anomaly_detector.py) to read directly from the queryable event store in shatrubodh.db (Phase 2).

Date/Time: 2026-06-21 18:45 (IST)
Files Modified: src/storage/database.py, DEVELOPMENT_LOG.md (Created: src/feature_engineering/behavior_profiles.py)
Reason: Implement Phase 2 Feature Engineering layer to aggregate raw logs into User-Day Behavioral Profiles (DRDO Requirement 3 prep).
Changes Implemented:
  - Added behavior_profiles table schema definition and composite optimization indexes to database initialization script.
  - Created insert_behavior_profiles bulk transactional writer inside database.py.
  - Implemented behavior_profiles.py aggregator utilizing registered custom scalar callbacks (extract_email_size, has_attachments, time_to_hours) to construct chunked aggregates.
  - Engineered 12 activity metric counts and 2 time-boundary variables (first/last activity decimal hours), storing them with role and department contexts.
Dependencies Added: None (pandas, sqlite3, os, sys)
Known Issues: None
Next Recommended Step: Design the Analytics layer (Isolation Forest & Local Outlier Factor) to process behavior_profiles records.

Date/Time: 2026-06-21 19:40 (IST)
Files Modified: src/analytics/anomaly_detector.py, src/storage/database.py, DEVELOPMENT_LOG.md
Reason: Implement Phase 5 Analytics layer to detect behavioral anomalies from user daily profiles (DRDO Requirement 3).
Changes Implemented:
  - Configured database schema for `anomaly_scores` table and composite indexes in `database.py`.
  - Upgraded `anomaly_detector.py` to ingest user day profiles from `behavior_profiles` SQLite table.
  - Implemented `IsolationForest` (contamination=0.02, random_state=42) trained on 14 raw numeric features.
  - Implemented `LocalOutlierFactor` (novelty=True, n_neighbors=20) trained on scaled numeric features (StandardScaler applied).
  - Designed combined score generation: raw IF/LOF scores are inverted (high value = anomalous), normalized [0, 1] using MinMaxScaler, combined 50/50, and scaled [0, 100].
  - Set binary `is_anomaly` flag based on the 98th percentile combined score threshold from the training set.
  - Modified the pipeline entry point to run database table initialization, train model parameters, score all profile days, and insert scores into SQLite.
Dependencies Added: None (scikit-learn, joblib)
Known Issues: None
Next Recommended Step: Ready for production use of analytics engine and integration with visual dashboard layer.

Date/Time: 2026-06-21 20:35 (IST)
Files Modified: src/storage/database.py, DEVELOPMENT_LOG.md (Created: src/analytics/risk_engine.py)
Reason: Implement Phase 6 Risk Engine layer to map statistical anomalies into human-interpretable risk scores and bands (DRDO Module 3 integration).
Changes Implemented:
  - Added `risk_scores` table schema, index definitions, and `insert_risk_scores` bulk transactional writer to `database.py`.
  - Created `risk_engine.py` to ingest anomaly scores and behavior profile context via SQLite.
  - Implemented vectorized math calculation of Context Multiplier (M) using weighted severity bounds (0.40 USB copy, 0.35 email data exfil, 0.25 after-hours shift logins) and 50MB email threshold cap.
  - Designed final Risk Score mapping using the headroom-scaling formula ($R = S_{raw} + (100 - S_{raw}) * (M - 1.0)$) to prevent ceiling truncation/excessive clipping near 100.
  - Coded vectorized condition banding ('Low', 'Medium', 'High', 'Critical') and generated verbose human-readable reasons explaining driver statistics.
  - Implemented command line entry point to automate scoring and database insertion for all 472,744 behavior profiles.
Dependencies Added: None (pandas, numpy, sqlite3, os, sys)
Known Issues: None
Next Recommended Step: Establish the Alert Generation layer to query critical risk profiles from SQLite database.

Date/Time: 2026-06-21 21:00 (IST)
Files Modified: src/storage/database.py, DEVELOPMENT_LOG.md (Created: src/analytics/alert_generator.py)
Reason: Implement Phase 7 Alert Generation layer to prioritize critical threat profiles into lifecycle-managed alerts (DRDO Module 4 integration).
Changes Implemented:
  - Added `alerts` table schema definition and optimized query indexes (`idx_alerts_status_severity`, `idx_alerts_user_date`) to `database.py`.
  - Implemented `insert_alerts` bulk transactional database writer utilizing SQLite's WAL mode and INSERT OR IGNORE conflict resolution logic.
  - Created `alert_generator.py` to ingest new risk scores above threshold (risk_score >= 50.0) that do not already have associated alerts.
  - Designed vectorized severity categorizations mapping scores to `Medium` (50.0–70.0), `High` (70.0–85.0), and `Critical` (>= 85.0) bands.
  - Configured vectorized mapping to serialize the complete daily behavior profile record (all 19 columns) into `evidence_json` for comprehensive SOC incident context and forensic auditability.
  - Verified pipeline generated 7,570 alerts (1 Critical, 432 High, 7,137 Medium) with verified database deduplication.
Dependencies Added: None (pandas, numpy, sqlite3, os, sys, uuid, datetime, json)
Known Issues: None
Next Recommended Step: Pipeline ready for Streamlit dashboard integration and analyst operational workflows.

Date/Time: 2026-07-01 00:40 (IST)
Files Modified: DEVELOPMENT_LOG.md
Reason: Document completion of Phase 8.1 - Operational SOC Dashboard Integration.
Changes Implemented:
  - Documented completion of Phase 8.1.
  - Objective: Integrate the operational Streamlit SOC dashboard with the existing UEBA backend pipeline while preserving the original Shatrubodh visual identity.
  - Completed Components:
    * Dashboard tab: Alert triage queue, severity/status filtering, user search, alert investigation panel, analyst feedback workflow, and alert status updates.
    * Threat Hunter tab: User identity lookup, alert history retrieval, user rolling baseline comparison, department-role cohort comparison, risk timeline visualization, and historical activity exploration.
    * Reports tab: Department threat density analysis, role anomaly distributions, and CSV export functionality.
  - Backend integrations reused: db_service.py, evidence_parser.py.
  - Major engineering decisions:
    * Rolled back to stable Phase 7 backend after dashboard redesign failure.
    * Rebuilt dashboard incrementally while preserving original visual design language.
    * Adopted rolling 30-record user baselines.
    * Adopted 90-day department-role cohort baselines.
    * Performed statistical aggregation in Python rather than SQLite.
  - Validation status: Dashboard startup (PASS), Database integration (PASS), Alert workflow (PASS), Threat hunter workflow (PASS), Reporting workflow (PASS).
  - Git milestone: Commit ffac270, Tag v0.8.1.
Dependencies Added: None
Known Issues: None
Next Recommended Step: Proceed to Phase 9: Validation, Verification, Vulnerability Assessment, and Code Hardening.
