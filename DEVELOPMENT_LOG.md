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

