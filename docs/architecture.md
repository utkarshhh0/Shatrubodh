# Shatrubodh Architecture

## Overview

Shatrubodh is a modular User and Entity Behavior Analytics (UEBA) platform designed to detect insider threats through behavioral analysis, unsupervised machine learning, contextual risk assessment, and analyst-assisted investigations.

The system follows a layered architecture where each module has a clearly defined responsibility and communicates through well-defined interfaces. This separation simplifies maintenance, testing, and future extension while keeping the analytics pipeline independent from the presentation layer.

---

# High-Level Architecture

```text
                    Raw Security Events
                            │
                            ▼
                     Data Collectors
                            │
                            ▼
                   Event Normalization
                            │
                            ▼
                     SQLite Data Store
                            │
                            ▼
              Behavior Profile Generation
                            │
                            ▼
        Isolation Forest + Local Outlier Factor
                            │
                            ▼
                   Contextual Risk Engine
                            │
                            ▼
                     Alert Generation
                            │
                            ▼
                  Streamlit SOC Dashboard
```

---

# Architectural Principles

Shatrubodh was developed around the following engineering principles:

- Modular architecture with clearly separated responsibilities.
- Database-driven workflows rather than in-memory pipelines.
- Explainable behavioral analytics instead of black-box scoring.
- Stateless dashboard components consuming service-layer APIs.
- Parameterized database queries for operational safety.
- Reproducible machine learning pipeline.
- Incremental hardening through validation and security reviews.

---

# System Layers

## 1. Data Collection Layer

Responsible for collecting raw security events from multiple enterprise sources.

Responsibilities:

- Parse security log sources.
- Collect authentication events.
- Collect endpoint activity.
- Gather directory service metadata.
- Produce unified raw events.

Output:

- Raw normalized event records.

---

## 2. Event Normalization Layer

Converts heterogeneous log formats into a consistent internal schema.

Responsibilities:

- Validate incoming events.
- Normalize timestamps.
- Standardize event fields.
- Attach identity context.
- Reject malformed records.

Output:

- Canonical security events.

---

## 3. Storage Layer

Stores normalized events and derived analytics in SQLite.

Responsibilities:

- Database initialization.
- Schema management.
- Index management.
- Bulk insertion.
- Transaction handling.

Primary tables include:

- users
- events
- behavior_profiles
- risk_scores
- alerts

---

## 4. Feature Engineering Layer

Transforms normalized events into behavioral profiles suitable for machine learning.

Responsibilities:

- Aggregate user activity.
- Compute daily behavioral metrics.
- Generate feature vectors.
- Preserve historical timelines.

Behavioral metrics include examples such as:

- Logon activity
- USB usage
- File operations
- Email activity
- Endpoint diversity
- Total event volume

---

## 5. Analytics Layer

Performs anomaly detection using unsupervised learning.

Models:

- Isolation Forest
- Local Outlier Factor (LOF)

Responsibilities:

- Model training.
- Model persistence.
- Feature scaling.
- Prediction.
- Anomaly scoring.

The analytics layer produces numerical anomaly scores without assigning operational risk.

---

## 6. Risk Engine

Converts anomaly scores into operational risk.

Responsibilities:

- Apply contextual multipliers.
- Weight behavioral indicators.
- Compute final risk score.
- Assign severity bands.

This separation ensures that statistical anomalies are interpreted within operational context before alert generation.

---

## 7. Alert Generation Layer

Generates actionable security alerts.

Responsibilities:

- Apply alert thresholds.
- Package evidence.
- Store alert metadata.
- Preserve analyst context.

Each alert contains:

- User identifier
- Timestamp
- Risk score
- Severity
- Evidence snapshot
- Investigation status
- Analyst notes

---

## 8. Dashboard Layer

Provides an operational interface for analysts.

Modules:

### Alert Triage

Capabilities:

- Alert queue
- Severity filtering
- Status filtering
- Analyst assignment
- Investigation notes

---

### Threat Hunter

Capabilities:

- Identity lookup
- Behavioral baseline comparison
- Cohort comparison
- Risk timeline
- Historical profile analysis

---

### Reports

Capabilities:

- Department threat distribution
- Role analytics
- CSV export
- Operational reporting

---

# Data Flow

```text
Security Logs
      │
      ▼
Collectors
      │
      ▼
Normalization
      │
      ▼
SQLite Database
      │
      ▼
Behavior Profiles
      │
      ▼
Analytics Models
      │
      ▼
Risk Engine
      │
      ▼
Alerts
      │
      ▼
SOC Dashboard
```

---

# Module Responsibilities

| Module | Responsibility |
|---------|----------------|
| collectors | Event acquisition |
| normalizers | Schema normalization |
| storage | Database management |
| feature_engineering | Behavioral profile generation |
| analytics | Machine learning models |
| risk_engine | Context-aware risk scoring |
| alert_generator | Alert creation |
| dashboard | Analyst interface |

---

# Database Design

The platform uses SQLite as its operational datastore.

Reasons for selection:

- Lightweight deployment.
- ACID-compliant transactions.
- Simple portability.
- Sufficient performance for research and prototype environments.
- Minimal operational overhead.

Parameterized SQL queries are used throughout the service layer to reduce injection risk and simplify query management.

---

# Security Considerations

The architecture incorporates several security-focused design decisions:

- Parameterized SQL queries.
- Layered separation between UI and database.
- Defensive input validation.
- Exception boundaries around service interfaces.
- Cached read-only analytics.
- Repository hardening.
- Environment isolation.

---

# Validation & Hardening

The architecture has undergone structured validation including:

- Architecture verification.
- Database validation.
- SQL query auditing.
- Adversarial input testing.
- Performance benchmarking.
- Exception boundary hardening.
- Defensive validation.
- Repository and environment hardening.

---

# Extensibility

The modular design allows future enhancements without significant architectural changes.

Potential extensions include:

- Live log ingestion.
- Threat intelligence integration.
- SIEM interoperability.
- Distributed database support.
- Additional anomaly detection models.
- REST API exposure.
- Containerized deployment.

---

# Conclusion

Shatrubodh adopts a modular UEBA architecture that separates data acquisition, behavioral analytics, contextual risk assessment, alert generation, and analyst workflows into independent layers. This separation improves maintainability, supports future expansion, and enables the platform to evolve from a research prototype toward an operational insider threat detection system.