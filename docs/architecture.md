# Shatrubodh Architecture Context

## Origin

Shatrubodh is an AI-Assisted User and Entity Behaviour Analytics (UEBA) system developed from a Defence Research and Development Organisation (DRDO) Smart India Hackathon problem statement under the Ministry of Defence.

The objective is to identify potential insider threats by analysing behavioural patterns across users, devices, files, communications and organisational context.

---

## Project Status

Current Status: Prototype / MVP

The original prototype used synthetic behavioural data generated through Faker and basic anomaly detection.

The project is now being upgraded to use a curated subset of the CMU CERT Insider Threat Dataset to provide a more realistic and defensible UEBA pipeline.

Legacy implementation artifacts are preserved under the `legacy/` directory for reference only and must not be used as active data sources.

---

## DRDO UEBA Requirements

The implementation must remain aligned with the original DRDO problem statement.

Required modules:

1. Data Collection
2. Data Normalization
3. Data Analytics
4. Alert Generation

All architectural decisions should map to one or more of these modules.

---

## Current Dataset

Timeline Window:

2010-12-01 to 2011-05-31

Available Data Sources:

* users.csv
* logon_filtered.csv
* device_filtered.csv
* file_filtered.csv
* email_filtered.csv
* LDAP snapshots (December 2010 to May 2011)

Excluded Sources:

* psychometric.csv
* http.csv

These datasets are excluded from the current implementation scope.

---

## Architectural Principles

* Preserve the existing Streamlit-based workflow.
* Do not redesign the project from scratch.
* Do not introduce Generative AI or LLM components.
* Do not introduce cloud services.
* Do not introduce unnecessary enterprise features.
* Maintain a modular architecture.
* Evolve the existing prototype rather than replacing it.

---

## Implementation Goal

Transform the current prototype into a realistic UEBA MVP by implementing:

* Data Collection
* Data Normalization
* Structured Storage
* Behavioural Analytics
* Risk-Based Alert Generation

while preserving the original project vision and workflow.