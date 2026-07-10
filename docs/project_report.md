# Project Report

---

# Table of Contents

- [Abstract](#abstract)
- [1. Introduction](#1-introduction)
- [2. Problem Statement](#2-problem-statement)
- [3. Objectives](#3-objectives)
- [4. Background](#4-background)
- [5. System Architecture](#5-system-architecture)
- [6. Dataset](#6-dataset)
- [7. Data Collection & Normalization](#7-data-collection--normalization)
- [8. Feature Engineering & Behavioral Profiling](#8-feature-engineering--behavioral-profiling)
- [9. Anomaly Detection & Machine Learning](#9-anomaly-detection--machine-learning)
- [10. Contextual Risk Assessment & Alert Generation](#10-contextual-risk-assessment--alert-generation)
- [11. Security Operations Center (SOC) Dashboard](#11-security-operations-center-soc-dashboard)
- [12. Validation, Verification & Security Hardening](#12-validation-verification--security-hardening)
- [13. Performance Evaluation](#13-performance-evaluation)
- [14. Engineering Decisions & Design Rationale](#14-engineering-decisions--design-rationale)
- [15. Limitations](#15-limitations)
- [16. Future Work](#16-future-work)
- [17. Conclusion](#17-conclusion)
- [18. References](#18-references)
- [Appendix A – Project Statistics](#appendix-a--project-statistics)

---

# Abstract

Insider threats represent one of the most challenging cybersecurity problems because malicious activities are often performed by trusted users operating with legitimate credentials, making them difficult to distinguish from normal organizational behavior. Traditional security solutions predominantly rely on predefined signatures, static rules, and known attack patterns, limiting their ability to identify subtle behavioral deviations associated with insider misuse, compromised accounts, or Advanced Persistent Threats (APTs).

Shatrubodh is a production-hardened **User and Entity Behavior Analytics (UEBA)** platform developed to address this challenge through behavioral modelling, unsupervised machine learning, contextual risk assessment, and analyst-assisted investigation workflows. The system aligns with the DRDO problem statement on **"User and Entity Behaviour Analytics (UEBA) for Internal Threat Identification"** by implementing a complete end-to-end behavioral analytics pipeline consisting of data collection, event normalization, behavioral profile generation, anomaly detection, contextual risk scoring, alert generation, and an operational Security Operations Center (SOC) dashboard.

Security events collected from enterprise data sources are normalized into a unified schema before being transformed into fourteen-dimensional daily behavioral profiles representing authentication activity, endpoint usage, removable media interactions, email behavior, workstation diversity, and temporal characteristics. These behavioral vectors are analysed using an ensemble of **Isolation Forest** and **Local Outlier Factor (LOF)** models to establish behavioral baselines and identify statistically significant deviations. The resulting anomaly scores are subsequently enriched by a contextual risk engine that incorporates operational indicators such as USB activity, email exfiltration volume, and after-hours access to produce explainable risk scores and actionable security alerts.

To support operational investigations, the platform provides an interactive SOC dashboard comprising alert triage, forensic threat hunting, historical behavioral analysis, peer cohort comparison, organizational reporting, and evidence-driven investigation workflows. Beyond functional implementation, the system has undergone structured validation, security auditing, defensive input validation, exception boundary hardening, repository hardening, and performance verification to improve reliability, maintainability, and deployment readiness.

Shatrubodh demonstrates how modular behavioral analytics, contextual risk modelling, and explainable machine learning can be integrated into a lightweight yet extensible UEBA platform capable of supporting insider threat detection while providing transparent analytical workflows suitable for research, cybersecurity education, and future enterprise-scale enhancement.

---

# 1. Introduction

Modern organizations generate enormous volumes of digital activity through authentication systems, endpoints, email platforms, file servers, removable media, and enterprise applications. While this digital footprint provides valuable visibility into organizational operations, it also introduces significant cybersecurity challenges, particularly in identifying malicious activities performed by trusted users. Unlike external attacks, insider threats often originate from individuals who possess legitimate access privileges, allowing their actions to closely resemble normal operational behavior and making them considerably more difficult to detect using conventional security mechanisms.

Traditional security solutions such as signature-based detection systems, rule-driven monitoring platforms, and conventional Security Information and Event Management (SIEM) solutions are primarily designed to identify known attack patterns, malware, network intrusions, and policy violations. Although highly effective against external threats, these approaches frequently struggle to identify gradual behavioral deviations, privilege misuse, compromised accounts, data exfiltration, or other forms of insider abuse that evolve over extended periods without violating predefined detection rules.

User and Entity Behavior Analytics (UEBA) has emerged as an important analytical approach to addressing this limitation. Instead of relying solely on static rules, UEBA establishes behavioral baselines for users and entities by analysing historical activity patterns and identifying statistically significant deviations that may indicate suspicious behavior. By combining behavioral profiling, machine learning, and contextual analysis, UEBA enables organizations to detect potential insider threats earlier while reducing dependence on manually maintained detection signatures.

Shatrubodh was developed in response to the Defence Research and Development Organisation (DRDO) problem statement titled **"User and Entity Behaviour Analytics (UEBA) for Internal Threat Identification."** The objective was to design and implement a complete behavioral analytics platform capable of collecting security telemetry, normalizing heterogeneous data sources, generating behavioral profiles, detecting anomalies using unsupervised machine learning, assessing contextual operational risk, generating actionable alerts, and providing analysts with an integrated Security Operations Center (SOC) dashboard for investigation and decision support.

To achieve these objectives, Shatrubodh adopts a modular architecture comprising dedicated layers for data collection, event normalization, database management, feature engineering, anomaly detection, contextual risk scoring, alert generation, and visualization. The analytics pipeline combines Isolation Forest and Local Outlier Factor (LOF) algorithms to establish behavioral baselines and identify anomalous user activity, while a contextual risk engine enriches statistical anomaly scores using operational indicators such as removable media usage, email exfiltration activity, and after-hours authentication patterns. The resulting alerts are presented through an interactive SOC dashboard that supports analyst triage, forensic threat hunting, historical behavioral analysis, organizational reporting, and evidence-driven investigations.

Beyond implementing the required analytical pipeline, the project emphasizes engineering quality through modular software design, database optimization, defensive programming, structured validation, security auditing, exception boundary hardening, repository hardening, and performance optimization. These design decisions ensure that the platform not only satisfies the functional requirements of a UEBA system but also provides a robust foundation for future research, educational use, and enterprise-scale enhancement.

This report presents the complete engineering journey behind Shatrubodh, including the problem motivation, architectural design, implementation methodology, machine learning pipeline, contextual risk model, validation strategy, security hardening measures, performance evaluation, engineering decisions, and opportunities for future development.

---

# 2. Problem Statement

The increasing digitalization of modern organizations has significantly expanded the volume of user interactions across enterprise networks, cloud platforms, endpoints, email systems, removable storage devices, and business applications. While these technologies improve operational efficiency, they also increase the complexity of monitoring user activities and identifying malicious behavior originating from within the organization.

Unlike external cyberattacks, insider threats are executed by users who possess legitimate credentials and authorized access to organizational resources. Such users may intentionally misuse their privileges or operate through compromised accounts, making their activities difficult to distinguish from legitimate operational behavior. Consequently, conventional security solutions based primarily on predefined signatures, static detection rules, or known Indicators of Compromise (IoCs) often fail to identify gradual behavioral deviations associated with insider threats.

As organizational infrastructures continue to grow, the quantity of generated security logs increases beyond the scale that can be effectively monitored through manual analysis. The adoption of hybrid cloud environments, remote work, privileged access management, and third-party integrations further complicates visibility across enterprise ecosystems, increasing the need for automated behavioral analysis capable of identifying subtle anomalies within large volumes of operational data.

Recognizing this challenge, the Defence Research and Development Organisation (DRDO), Ministry of Defence, proposed the problem statement **"User and Entity Behaviour Analytics (UEBA) for Internal Threat Identification."** The expected solution defines an end-to-end analytical pipeline consisting of four primary stages:

- Collection of security telemetry from enterprise systems, applications, endpoints, servers, and network infrastructure.
- Normalization of heterogeneous security events into a unified representation suitable for analysis.
- Behavioral analytics using machine learning and statistical techniques to establish normal behavioral baselines and identify significant deviations.
- Generation of anomaly alerts whenever suspicious or potentially malicious behavior is detected.

Shatrubodh was developed as a comprehensive implementation of this problem statement. Rather than relying solely on anomaly detection, the platform extends the proposed pipeline through contextual risk assessment, explainable behavioral evidence, analyst-driven investigation workflows, historical baseline comparisons, peer cohort analysis, and an operational Security Operations Center (SOC) dashboard. These additions transform statistical anomaly detection into actionable cybersecurity intelligence that can support security analysts during insider threat investigations while maintaining a modular and extensible system architecture suitable for future enterprise deployment.

---

# 3. Objectives

The primary objective of Shatrubodh is to design and implement a modular User and Entity Behaviour Analytics (UEBA) platform capable of identifying potential insider threats by analysing behavioral deviations within enterprise environments. The platform aims to transform large volumes of heterogeneous security telemetry into meaningful analytical insights that assist security analysts in detecting suspicious activities while reducing dependence on static rule-based detection mechanisms.

To achieve this objective, the project establishes the following engineering goals:

## Primary Objectives

- Develop a complete end-to-end UEBA pipeline covering data collection, normalization, behavioral analytics, risk assessment, alert generation, and analyst investigation.
- Establish behavioral baselines for users through historical activity profiling rather than predefined detection signatures.
- Detect anomalous user behavior using unsupervised machine learning techniques suitable for previously unseen attack patterns.
- Convert statistical anomaly scores into operationally meaningful risk scores using contextual behavioral indicators.
- Present investigation results through an intuitive Security Operations Center (SOC) dashboard supporting alert triage, forensic analysis, and reporting.

## Technical Objectives

- Design a modular architecture with clearly separated functional layers.
- Normalize heterogeneous security events into a unified internal schema.
- Generate daily behavioral profiles using engineered activity metrics.
- Implement an anomaly detection ensemble using Isolation Forest and Local Outlier Factor (LOF).
- Persist analytical results within a relational database supporting efficient querying and reporting.
- Build reusable service layers between the database and visualization components.
- Ensure explainability by preserving behavioral evidence for every generated alert.

## Engineering Objectives

- Maintain clear separation between analytics, storage, and presentation layers.
- Implement parameterized database operations to improve security and maintainability.
- Design reusable modules capable of future integration with additional data sources.
- Optimize database access through indexing and caching mechanisms.
- Improve operational robustness through structured validation, defensive programming, and exception boundary handling.
- Maintain reproducibility through deterministic model training and documented dependencies.

## Operational Objectives

- Support analyst-driven alert investigation rather than automated decision making.
- Enable comparison of user behavior against both historical baselines and peer cohorts.
- Provide organizational threat visibility through departmental and role-based reporting.
- Allow export of investigation results for operational reporting and further analysis.

Collectively, these objectives guided the development of Shatrubodh from an initial research prototype into a production-hardened UEBA platform that combines behavioral analytics, contextual risk assessment, and operational investigation workflows within a unified architecture.

---

# 4. Background

The rapid digital transformation of modern organizations has fundamentally changed the cybersecurity landscape. Enterprise environments now consist of interconnected authentication systems, endpoints, email platforms, cloud services, databases, and business applications that collectively generate vast volumes of security telemetry. While this extensive digital footprint enables organizations to operate more efficiently, it also increases the complexity of monitoring user activities and identifying malicious behavior occurring within trusted network boundaries.

Historically, cybersecurity solutions have focused primarily on defending against external adversaries through mechanisms such as firewalls, intrusion detection systems (IDS), antivirus software, endpoint protection platforms, and signature-based monitoring. These technologies are highly effective at identifying known attack patterns, malware signatures, and policy violations. However, they are considerably less effective against insider threats, where malicious actions are performed using legitimate credentials and authorized access privileges.

An insider threat refers to any security risk originating from an individual or entity that possesses authorized access to organizational resources and intentionally or unintentionally compromises the confidentiality, integrity, or availability of those resources. Such threats may arise from malicious employees, compromised user accounts, negligent users, contractors, third-party vendors, or privileged administrators. Because these actors operate within normal access boundaries, their activities often appear legitimate, making traditional rule-based detection approaches insufficient for identifying subtle behavioral deviations.

The challenge becomes significantly greater as organizations continue to expand their digital infrastructure. Modern enterprises generate millions of authentication events, file operations, email transactions, endpoint activities, and network interactions each day. Manual inspection of this continuously growing telemetry is neither practical nor scalable. Consequently, organizations increasingly rely on automated behavioral analytics to identify suspicious patterns that would otherwise remain undetected.

User and Entity Behaviour Analytics (UEBA) has emerged as a specialized cybersecurity discipline designed to address these limitations. Unlike conventional security solutions that depend primarily on predefined detection rules or known indicators of compromise, UEBA establishes behavioral baselines by analysing historical user activity and identifying statistically significant deviations from expected behavior. Rather than searching exclusively for known attack signatures, UEBA focuses on recognizing unusual behavioral patterns that may indicate privilege misuse, compromised accounts, insider abuse, data exfiltration, or the early stages of Advanced Persistent Threats (APTs).

A typical UEBA platform consists of several interconnected analytical stages. Security events are collected from multiple enterprise sources before being normalized into a unified schema suitable for downstream processing. Feature engineering techniques transform normalized events into structured behavioral profiles representing user activity over defined observation periods. Machine learning algorithms analyse these behavioral profiles to distinguish expected behavior from anomalous activity, after which contextual information is incorporated to determine the operational significance of detected anomalies. Finally, actionable alerts are generated to support security analysts during investigation and incident response.

Among the various machine learning approaches employed in UEBA systems, unsupervised learning has become particularly important because accurately labelled insider threat datasets are rarely available in operational environments. Algorithms such as Isolation Forest and Local Outlier Factor (LOF) enable behavioral anomaly detection without requiring prior knowledge of malicious activities by learning statistical characteristics of normal user behavior and identifying observations that deviate significantly from established behavioral baselines.

However, anomaly detection alone is insufficient for practical cybersecurity operations. Not every statistical anomaly represents malicious activity, and many legitimate business operations may temporarily deviate from historical patterns. Modern UEBA platforms therefore combine statistical anomaly detection with contextual risk assessment, behavioral evidence, historical comparisons, and analyst-driven investigation workflows to improve explainability and reduce false positives. This integration enables security teams to prioritize investigations based on operational risk rather than statistical deviation alone.

Shatrubodh was developed within this context as a comprehensive implementation of the UEBA paradigm. Rather than functioning solely as a machine learning model, the platform integrates data collection, event normalization, behavioral profiling, anomaly detection, contextual risk scoring, alert generation, and an operational Security Operations Center (SOC) dashboard into a unified analytical workflow. The resulting system demonstrates how behavioral analytics, explainable machine learning, and modular software engineering can be combined to support effective insider threat detection while maintaining transparency, extensibility, and operational usability.

---

# 5. System Architecture

Shatrubodh adopts a modular layered architecture that separates data acquisition, data processing, behavioral analytics, risk assessment, alert generation, and visualization into independent functional components. This architectural approach improves maintainability, extensibility, testability, and fault isolation while allowing each subsystem to evolve independently without affecting the remainder of the platform.

Rather than treating anomaly detection as a standalone machine learning problem, the platform implements a complete behavioral analytics pipeline that transforms raw enterprise security telemetry into actionable intelligence for security analysts. Each layer performs a specific responsibility and exposes well-defined interfaces to subsequent stages, resulting in a structured and reproducible workflow.

The overall processing pipeline is illustrated below.

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

The architecture is organized into the following functional layers.

## 5.1 Data Collection Layer

The data collection layer is responsible for ingesting raw organizational telemetry from enterprise data sources. Dedicated collectors extract security events and organizational metadata before forwarding them for normalization.

Current collectors include:

- CERT event collector
- LDAP user information collector

The separation of collectors from downstream processing enables additional enterprise log sources to be integrated without requiring modifications to the analytics pipeline.

---

## 5.2 Event Normalization Layer

Security events originating from different systems frequently contain inconsistent field names, timestamp formats, and metadata structures. The normalization layer converts heterogeneous inputs into a unified internal schema suitable for downstream processing.

Primary responsibilities include:

- Schema validation
- Timestamp normalization
- Field standardization
- Identity context enrichment
- Event validation

The resulting canonical event structure allows all downstream analytical components to operate independently of the original data source.

---

## 5.3 Storage Layer

Normalized events are stored within a relational SQLite database that serves as the central data repository for the platform.

The storage layer manages:

- Database initialization
- Schema creation
- Index management
- Transaction handling
- Bulk data insertion
- Query execution

The database contains six operational tables:

- users
- events
- behavior_profiles
- anomaly_scores
- risk_scores
- alerts

Strategically placed indexes improve query performance for dashboard rendering, filtering, and analyst investigations while SQLite's Write-Ahead Logging (WAL) mode provides reliable transactional behavior.

---

## 5.4 Feature Engineering Layer

Raw security events are transformed into behavioral profiles representing daily user activity.

Instead of analysing individual events directly, the system aggregates security telemetry into fourteen behavioral metrics describing authentication patterns, endpoint activity, removable media usage, email behavior, workstation diversity, and temporal activity boundaries.

Behavioral aggregation significantly reduces data dimensionality while preserving meaningful indicators required for anomaly detection.

---

## 5.5 Analytics Layer

The analytics layer performs behavioral anomaly detection using an ensemble of two complementary unsupervised machine learning algorithms.

Isolation Forest identifies globally anomalous behavioral profiles by isolating observations requiring fewer partitioning operations.

Local Outlier Factor (LOF) identifies locally anomalous observations by comparing the density of each behavioral profile against its surrounding neighborhood.

Both models operate without requiring labelled insider threat examples, making the approach suitable for realistic enterprise environments where malicious samples are scarce.

The normalized outputs of both algorithms are combined to produce a unified anomaly score representing the statistical abnormality of each behavioral profile.

---

## 5.6 Contextual Risk Engine

Statistical anomalies alone are insufficient to determine operational risk.

The Risk Engine enriches anomaly scores by incorporating contextual behavioral indicators including:

- USB file copying
- Email attachment exfiltration
- After-hours authentication activity

These contextual multipliers produce an operational risk score together with a corresponding severity classification and human-readable explanation suitable for analyst interpretation.

---

## 5.7 Alert Generation Layer

Behavioral profiles exceeding the configured operational threshold are promoted into security alerts.

Each alert preserves:

- User identity
- Behavioral evidence
- Risk score
- Severity
- Investigation status
- Assigned analyst
- Analyst notes

This evidence-driven design ensures that every alert remains fully traceable throughout the investigation lifecycle.

---

## 5.8 Security Operations Center Dashboard

The final architectural layer provides a unified interface for analysts to investigate behavioral anomalies.

The dashboard consists of three operational modules.

### Alert Triage

Provides:

- Alert queue
- Severity filtering
- Status filtering
- User search
- Analyst assignment
- Investigation workflow

### Threat Hunter

Provides:

- User demographics
- Historical behavioral analysis
- Peer cohort comparison
- Risk timeline visualization
- Statistical deviation analysis

### System & Reports

Provides:

- Organizational threat analytics
- Department distributions
- Role distributions
- CSV export
- Operational reporting

---

## 5.9 Architectural Characteristics

The architecture was designed around several engineering principles:

- Modular separation of responsibilities.
- Layered processing pipeline.
- Database-centric data management.
- Explainable behavioral analytics.
- Reproducible machine learning workflow.
- Context-aware risk assessment.
- Operational analyst support rather than automated decision making.
- Extensibility for future enterprise integrations.

These architectural principles collectively enable Shatrubodh to function as a complete UEBA platform rather than a standalone anomaly detection model, providing a scalable foundation for future research and operational enhancement.

---

# 6. Dataset

The effectiveness of a User and Entity Behaviour Analytics (UEBA) system depends largely on the quality and representativeness of the behavioural data used to establish normal user activity. Since obtaining real enterprise security logs is generally restricted due to privacy, confidentiality, and organizational security policies, publicly available research datasets provide an effective foundation for developing and evaluating behavioural analytics systems.

Shatrubodh was developed using the **CERT Insider Threat Dataset**, originally created by the **CERT Program at Carnegie Mellon University (CMU)**. During development, the dataset was obtained through a publicly available Kaggle mirror to facilitate reproducible experimentation while respecting the original dataset's distribution model.

Unlike conventional cybersecurity datasets that primarily focus on malware samples or network intrusion traffic, the CERT Insider Threat Dataset simulates realistic enterprise activity generated by employees over extended periods. The dataset models normal organizational operations as well as insider threat scenarios by recording user interactions across multiple enterprise systems, making it particularly suitable for behavioural analytics and insider threat detection research.

Although the complete CERT dataset contains numerous event sources and supporting files, Shatrubodh intentionally adopts a **selective data ingestion strategy** rather than processing the entire dataset. Only the datasets required by the implemented behavioural analytics pipeline were imported and processed.

The primary data sources utilized during development include:

- **logon_filtered** — user authentication and logon activity.
- **device_filtered** — workstation and removable device interactions.
- **file_filtered** — file access, creation, modification, deletion, and removable media file operations.
- **email_filtered** — organizational email communication and attachment activity.
- **users** — employee identity and organizational metadata.
- **LDAP** — enterprise directory information containing departments, roles, reporting hierarchy, managers, and team assignments.

This selective ingestion strategy significantly reduces unnecessary processing while preserving all behavioural indicators required for insider threat analysis. It also reflects realistic enterprise deployments where only relevant security telemetry is collected for behavioural modelling instead of indiscriminately processing every available log source.

The imported datasets are processed through dedicated ingestion modules within the platform. The CERT Collector is responsible for importing behavioural event logs, while the LDAP Collector enriches user identities with organizational context. Together, these collectors populate the normalized event repository that serves as the foundation for all downstream analytics.

Following ingestion, every imported record undergoes schema normalization. Since individual data sources differ in structure, field names, timestamp formats, and available metadata, the normalization layer converts heterogeneous records into a unified internal event schema. This standardized representation enables all downstream analytical components to operate independently of the original dataset format while ensuring consistency throughout the behavioural analytics pipeline.

Rather than applying machine learning directly to raw security events, Shatrubodh aggregates normalized events into **daily behavioural profiles**. Each profile summarizes a user's activity over a single observation period using a fourteen-dimensional feature vector engineered to capture meaningful behavioural characteristics across authentication patterns, endpoint usage, removable media activity, email behaviour, workstation diversity, and temporal activity.

This behavioural aggregation provides several engineering advantages. It substantially reduces data dimensionality, minimizes noise generated by isolated events, preserves long-term behavioural characteristics, and produces a consistent numerical representation suitable for unsupervised anomaly detection algorithms such as **Isolation Forest** and **Local Outlier Factor (LOF)**.

Throughout development, the CERT dataset served solely as a source of enterprise security telemetry. All event ingestion, normalization, feature engineering, behavioural aggregation, machine learning models, contextual risk scoring, alert generation, database design, visualization components, and investigation workflows were independently designed and implemented within the Shatrubodh platform.

## Dataset Source

**Original Dataset**

CERT Insider Threat Dataset  
CERT Program  
Carnegie Mellon University (CMU)

**Development Source**

Public Kaggle mirror used during development:

https://www.kaggle.com/datasets/mrajaxnp/cert-insider-threat-detection-research/

The dataset is **not redistributed** as part of this repository. Users wishing to reproduce the project should obtain the dataset from the above source (or an official distribution if available), place the required source files within the project's dataset directory, and execute the ingestion pipeline before running the behavioural analytics workflow.

---

# 7. Data Collection & Normalization

The primary objective of the data collection and normalization stage is to transform heterogeneous enterprise security logs into a consistent, machine-readable representation suitable for behavioural analytics. Since the CERT Insider Threat Dataset consists of multiple independent data sources with varying schemas and semantics, a preprocessing pipeline was developed to unify the collected information before any analytical operations are performed.

Rather than directly exposing raw dataset files to downstream components, Shatrubodh introduces a dedicated ingestion layer responsible for collecting, validating, enriching, and normalizing security telemetry. This design isolates dataset-specific processing from the remainder of the platform, allowing analytical modules to operate on a standardized event representation independent of the original source format.

## 7.1 Data Collection

Data acquisition is performed through two specialized collectors, each responsible for a distinct category of enterprise information.

### CERT Collector

The CERT Collector imports behavioural security events from the filtered CERT dataset files, including:

- User logon activity
- Device interaction events
- File system operations
- Email communication records

Each record is parsed, validated, and converted into the platform's internal event representation before being forwarded to the normalization pipeline.

### LDAP Collector

Behavioural analysis alone is insufficient without organizational context. The LDAP Collector imports enterprise identity information, including:

- Employee identifiers
- Department assignments
- Job roles
- Reporting managers
- Team affiliations

This contextual information is associated with behavioural events throughout the analytical pipeline, enabling organizational reporting and peer-group comparisons.

---

## 7.2 Event Normalization

Because each source file contains different field names, timestamp formats, and metadata structures, a normalization stage converts all collected records into a unified schema.

Normalization includes:

- Timestamp standardization
- User identity validation
- Event type mapping
- Missing value handling
- Data type conversion
- Field standardization

After normalization, every event follows a consistent internal structure regardless of its original source.

This abstraction significantly simplifies downstream processing because feature engineering, anomaly detection, database operations, and dashboard components no longer depend on dataset-specific formats.

---

## 7.3 Data Validation

Before events are accepted into the analytical pipeline, multiple validation checks are performed to improve data integrity.

Validation includes:

- Verification of mandatory fields
- Detection of malformed records
- Null value handling
- Invalid timestamp rejection
- User identity consistency checks

Records failing validation are safely ignored or handled through defensive processing to prevent pipeline failures while preserving overall dataset integrity.

---

## 7.4 Context Enrichment

After normalization, behavioural events are enriched using organizational metadata obtained from the LDAP directory.

This enrichment associates every event with organizational attributes such as department, role, reporting manager, and team membership.

Adding organizational context enables the platform to perform:

- Department-level analytics
- Role-based behavioural comparisons
- Peer cohort analysis
- Organizational threat reporting

These contextual attributes also contribute to investigation workflows presented within the Threat Hunter module.

---

## 7.5 Database Integration

Normalized and enriched events are persisted within the platform's SQLite database through the storage layer.

The storage subsystem maintains dedicated tables for:

- Users
- Events
- Behaviour Profiles
- Anomaly Scores
- Risk Scores
- Alerts

Parameterized SQL queries are used throughout the platform to improve security, while indexed database tables significantly reduce dashboard query latency during investigations and reporting.

---

## 7.6 Engineering Considerations

Several engineering decisions guided the implementation of the ingestion pipeline.

- Selective ingestion was adopted instead of processing the entire CERT dataset, reducing unnecessary computation while preserving all behavioural indicators required by the UEBA pipeline.
- Collection logic was separated from analytical modules to improve maintainability and allow future integration of additional enterprise log sources.
- Normalization was centralized to ensure every downstream component operates on a consistent event schema.
- Organizational metadata was incorporated during preprocessing rather than during visualization, reducing redundant database queries and simplifying analytical workflows.
- Defensive validation was implemented to improve robustness against malformed or incomplete records.

These design choices establish a reliable and reproducible data foundation upon which behavioural profiling, anomaly detection, contextual risk assessment, and analyst investigation are subsequently performed.

---

# 8. Feature Engineering & Behavioral Profiling

Raw security events rarely provide sufficient information for meaningful behavioural analysis when considered individually. A single authentication event, file access operation, or email transmission may appear entirely legitimate in isolation despite contributing to an abnormal behavioural pattern over time. Consequently, Shatrubodh employs a dedicated feature engineering pipeline that transforms normalized enterprise events into structured behavioural profiles suitable for machine learning.

Instead of analysing millions of independent security events, the platform aggregates user activities into daily behavioural summaries. Each behavioural profile represents the activities performed by a single user during a single observation period, capturing behavioural trends rather than isolated actions. This aggregation significantly reduces data dimensionality while preserving the behavioural characteristics required for anomaly detection.

## 8.1 Behavioural Profile Generation

Following event normalization, security events are grouped according to user identity and observation date. Events belonging to the same user within the same day are aggregated into a unified behavioural profile representing that user's operational activity for the selected period.

Each generated profile serves as the analytical unit processed throughout the remainder of the UEBA pipeline. This approach enables the anomaly detection models to evaluate complete behavioural patterns instead of isolated log entries.

The behavioural profile generation process also establishes a consistent feature space across all users, ensuring that every observation contains the same numerical representation regardless of the number or type of raw events originally collected.

---

## 8.2 Engineered Behavioural Features

Each behavioural profile consists of fourteen engineered numerical features designed to summarize the most significant indicators of insider activity.

The generated feature vector includes:

| Feature | Description |
|---------|-------------|
| Logon Count | Total successful authentication events recorded during the observation period. |
| Logoff Count | Total user logoff events. |
| After Hours Logins | Number of authentication events occurring outside normal working hours. |
| USB Insertions | Number of removable media insertion events. |
| File Write Count | Total file creation or modification operations. |
| File Copy To USB | Number of files copied to removable storage devices. |
| File Delete Count | Number of file deletion operations. |
| Emails Sent | Total outgoing email messages. |
| Attachments Sent | Number of email attachments transmitted. |
| Email Exfil Bytes | Total volume of outbound email data. |
| Unique PCs | Number of distinct workstations used by the employee. |
| Total Events | Aggregate behavioural activity recorded during the observation period. |
| First Activity Hour | Earliest recorded activity time for the day. |
| Last Activity Hour | Latest recorded activity time for the day. |

These features collectively describe authentication behaviour, workstation usage, removable media activity, file operations, communication behaviour, temporal activity, and overall operational workload.

---

## 8.3 Behavioural Baseline Construction

Rather than comparing users against predefined security rules, Shatrubodh establishes behavioural baselines directly from historical activity.

As behavioural profiles accumulate over time, the platform learns statistical representations of normal organizational behaviour. These baselines enable users to be evaluated relative to their own historical activity as well as against comparable peer groups within the organization.

This behavioural modelling approach allows the system to identify gradual deviations that may remain undetected by traditional signature-based security mechanisms.

---

## 8.4 Advantages of Behavioural Aggregation

Transforming raw security telemetry into behavioural profiles provides several engineering and analytical benefits.

The approach:

- Reduces the computational complexity associated with analysing millions of individual security events.
- Minimizes noise introduced by isolated operational activities.
- Produces a fixed-length numerical representation required by machine learning algorithms.
- Captures behavioural trends instead of isolated actions.
- Simplifies statistical comparison across users and observation periods.
- Enables explainable behavioural evidence to be presented during analyst investigations.

These advantages improve both analytical performance and operational interpretability.

---

## 8.5 Integration with the Analytics Pipeline

The generated behavioural profiles form the direct input to the anomaly detection layer.

Before model inference, each feature vector undergoes preprocessing and scaling consistent with the trained machine learning models. The resulting standardized behavioural profiles are then evaluated by the Isolation Forest and Local Outlier Factor (LOF) algorithms to determine their statistical deviation from established behavioural norms.

Because every downstream analytical component operates exclusively on behavioural profiles rather than raw events, the feature engineering layer serves as the critical bridge between enterprise security telemetry and intelligent behavioural analytics.

By converting heterogeneous security logs into structured behavioural representations, this stage enables Shatrubodh to perform scalable, explainable, and context-aware insider threat detection while maintaining a consistent analytical workflow across the entire platform.

---

# 9. Anomaly Detection & Machine Learning

The core analytical capability of Shatrubodh is its ability to identify behavioural deviations that may indicate potential insider threats. Since labelled insider threat data is scarce and real-world attack patterns are highly diverse, the platform adopts an unsupervised machine learning approach that learns normal behavioural characteristics directly from historical user activity without requiring predefined attack signatures.

Rather than classifying activities as malicious or benign, the analytical pipeline estimates how significantly a behavioural profile deviates from the established baseline. This enables the platform to identify previously unseen attack patterns while remaining independent of manually maintained detection rules.

## 9.1 Selection of Machine Learning Models

Shatrubodh employs an ensemble of two complementary unsupervised anomaly detection algorithms:

- Isolation Forest
- Local Outlier Factor (LOF)

These algorithms were selected because they detect anomalies using fundamentally different statistical principles, allowing the platform to capture both globally abnormal behaviour and locally unusual behavioural patterns.

The combination provides greater robustness than relying on a single anomaly detection technique.

---

## 9.2 Isolation Forest

Isolation Forest is an ensemble-based anomaly detection algorithm specifically designed to identify rare observations.

Instead of modelling normal behaviour explicitly, the algorithm repeatedly partitions the feature space using randomly generated decision trees. Behavioural profiles that require fewer partitions to become isolated are considered statistically anomalous because they occupy sparse regions of the feature space.

Within Shatrubodh, Isolation Forest provides a global assessment of behavioural abnormality across all engineered behavioural metrics.

Its primary advantages include:

- Efficient operation on large behavioural datasets.
- Independence from labelled training data.
- Robust performance in high-dimensional feature spaces.
- Linear scalability with increasing data volume.

---

## 9.3 Local Outlier Factor (LOF)

While Isolation Forest evaluates anomalies globally, Local Outlier Factor focuses on local behavioural density.

LOF compares each behavioural profile with its neighbouring observations. If a user's activity is significantly less dense than the surrounding behavioural cluster, that profile is considered locally anomalous.

This enables detection of subtle insider behaviours that may appear statistically normal across the organization but remain highly unusual within a comparable peer group.

LOF is particularly effective for identifying:

- Gradual behavioural drift.
- Department-specific anomalies.
- Localized deviations among similar users.
- Context-sensitive behavioural changes.

---

## 9.4 Ensemble Behavioural Analysis

Rather than depending exclusively on either algorithm, Shatrubodh combines the outputs of both models into a unified anomaly assessment.

Each behavioural profile is independently evaluated by Isolation Forest and Local Outlier Factor. The resulting anomaly scores are normalized before being incorporated into the subsequent contextual risk assessment stage.

This ensemble strategy reduces dependence on the limitations of individual algorithms while improving overall detection stability across diverse behavioural patterns.

---

## 9.5 Model Training

The anomaly detection models are trained exclusively on engineered behavioural profiles generated from normalized enterprise activity.

The training workflow consists of:

1. Behavioural profile generation.
2. Feature preprocessing and normalization.
3. Model fitting using unsupervised learning.
4. Model serialization using Joblib.
5. Persistent storage for future inference.

Once trained, the serialized models are reused during operational analysis without requiring retraining for every execution.

This design improves reproducibility while reducing computational overhead during deployment.

---

## 9.6 Behavioural Inference

During runtime, newly generated behavioural profiles follow the same preprocessing pipeline used during training.

Each profile is evaluated independently by both anomaly detection models. The resulting statistical outputs indicate the degree to which the observed behaviour deviates from established organizational norms.

These anomaly scores are intentionally treated as intermediate analytical outputs rather than final security decisions. Statistical deviation alone does not necessarily imply malicious activity and therefore requires contextual interpretation.

---

## 9.7 Engineering Considerations

Several engineering decisions guided the design of the analytical pipeline:

- Unsupervised learning eliminates the dependency on labelled insider threat datasets.
- Ensemble modelling improves robustness by combining complementary anomaly detection strategies.
- Model serialization enables reproducible deployment without repeated training.
- Separation of model inference from risk assessment improves modularity and maintainability.
- Statistical anomaly detection is intentionally decoupled from operational alert generation to reduce false positives.

This layered analytical design allows Shatrubodh to distinguish statistical behavioural deviations from operational security risks, enabling subsequent contextual analysis to determine the true significance of detected anomalies.

The anomaly detection layer therefore serves as the analytical foundation upon which the platform's contextual risk engine, alert generation pipeline, and analyst investigation workflows are built.

---

# 10. Contextual Risk Assessment & Alert Generation

Statistical anomaly detection provides an indication of behavioural deviation but does not necessarily imply malicious intent. Legitimate operational activities, changes in work responsibilities, or unusual business requirements may also produce statistically anomalous behavioural patterns. Consequently, Shatrubodh introduces a dedicated contextual risk assessment layer that transforms statistical anomaly scores into operationally meaningful security intelligence before alerts are generated.

This separation between anomaly detection and risk assessment is a fundamental architectural decision within the platform. Machine learning models are responsible only for identifying behavioural deviations, while the Risk Engine determines the operational significance of those deviations by incorporating additional contextual indicators relevant to insider threat detection.

## 10.1 Contextual Risk Assessment

Following anomaly detection, each behavioural profile is evaluated by the Risk Engine. Rather than relying exclusively on anomaly scores, the engine incorporates behavioural indicators commonly associated with insider threats to produce a comprehensive operational risk assessment.

The contextual evaluation considers factors including:

- Removable media (USB) activity.
- File transfers to removable storage.
- Email attachment activity.
- Outbound email data volume.
- Authentication outside normal working hours.
- Overall behavioural anomaly score.

Each indicator contributes to the overall assessment according to predefined analytical rules designed to prioritize behaviours that present greater organizational risk.

The resulting contextual analysis produces a normalized risk score representing the likelihood that the observed behavioural pattern requires analyst attention.

---

## 10.2 Risk Classification

To improve operational usability, numerical risk scores are translated into discrete severity levels.

Shatrubodh classifies detected behaviours into three operational categories:

- **Medium**
- **High**
- **Critical**

This classification enables analysts to prioritize investigations according to operational impact rather than manually interpreting numerical anomaly scores.

By separating statistical modelling from operational prioritization, the platform reduces analyst workload while preserving explainability throughout the investigation process.

---

## 10.3 Alert Generation

Once a behavioural profile exceeds the configured operational threshold, the Alert Generation module constructs a complete investigation record.

Each generated alert contains:

- User identifier.
- Timestamp.
- Behavioural evidence.
- Anomaly score.
- Contextual risk score.
- Severity classification.
- Investigation status.
- Assigned analyst.
- Investigation notes.

Rather than storing only numerical outputs, the alert preserves the behavioural evidence used during the assessment process. This enables analysts to understand why an alert was generated without requiring re-execution of the analytical pipeline.

---

## 10.4 Alert Lifecycle

Alerts progress through a structured investigation workflow designed to support operational Security Operations Center (SOC) activities.

The implemented investigation states include:

- **New**
- **In Progress**
- **Resolved**
- **False Positive**

These states allow analysts to track investigation progress while preserving historical records of security decisions and incident outcomes.

Additional investigation metadata, including analyst assignments and investigation notes, is maintained throughout the alert lifecycle to support collaborative analysis and operational auditing.

---

## 10.5 Explainable Security Analytics

One of the primary design goals of Shatrubodh is to ensure that generated alerts remain explainable.

Instead of presenting only anomaly scores, the platform provides supporting behavioural evidence including:

- Historical user baselines.
- Peer cohort comparisons.
- Behavioural deviation metrics.
- Contextual activity indicators.
- Timeline-based behavioural history.

This evidence-driven approach allows analysts to understand the factors contributing to each alert, improving confidence in analytical outcomes while supporting informed investigation decisions.

---

## 10.6 Engineering Considerations

Several engineering decisions guided the implementation of the contextual risk and alert generation pipeline.

- Statistical anomaly detection and operational risk assessment are intentionally separated into independent modules.
- Contextual behavioural indicators are incorporated only after machine learning inference to improve modularity and explainability.
- Alert generation preserves analytical evidence rather than only numerical scores.
- Investigation workflows are integrated directly into the platform to support analyst-centric operations instead of automated decision making.
- Operational severity classification simplifies alert prioritization without modifying underlying anomaly detection models.

By introducing contextual risk assessment between machine learning inference and alert generation, Shatrubodh bridges the gap between statistical anomaly detection and practical cybersecurity operations. This layered approach enables behavioural deviations to be interpreted within their operational context, producing actionable alerts that support efficient analyst investigations while reducing reliance on purely statistical decision making.

---

# 11. Security Operations Center (SOC) Dashboard

The Security Operations Center (SOC) Dashboard serves as the operational interface of Shatrubodh, enabling security analysts to monitor alerts, investigate suspicious user behaviour, perform forensic analysis, and generate organizational reports. Rather than functioning solely as a visualization layer, the dashboard integrates behavioural analytics, contextual risk assessment, historical evidence, and investigation workflows into a unified analyst-centric environment.

The dashboard is implemented using **Streamlit**, providing an interactive web-based interface that communicates with the underlying service layer and SQLite database. By separating presentation logic from analytics and storage components, the platform maintains a modular architecture while allowing future migration to alternative frontend technologies without affecting the analytical pipeline.

The dashboard is organized into three operational modules that collectively support the complete investigation lifecycle.

---

## 11.1 Alert Queue

The Alert Queue acts as the primary operational workspace for security analysts.

It provides a centralized view of all generated alerts together with their associated severity, investigation status, assigned analyst, and behavioural evidence.

Key capabilities include:

- Alert prioritization based on severity.
- Filtering by investigation status.
- User-specific alert search.
- Analyst assignment.
- Investigation note management.
- Alert status updates.

The dashboard allows analysts to progress alerts through the defined investigation workflow while preserving a complete audit trail of investigation activities.

---

## 11.2 Threat Hunter

The Threat Hunter module provides detailed behavioural analysis for individual users.

Rather than presenting only anomaly scores, this module enables analysts to understand *why* a behavioural profile was classified as suspicious.

Available analytical views include:

- User identity and organizational information.
- Historical behavioural timelines.
- Behavioural baseline comparisons.
- Peer cohort comparisons.
- Statistical deviation analysis.
- Daily behavioural profile history.
- Contextual evidence supporting risk assessment.

These capabilities allow analysts to distinguish between legitimate operational deviations and behaviours that warrant further investigation.

---

## 11.3 System & Reports

The reporting module provides an organizational view of behavioural risk across the enterprise.

Instead of focusing on individual users, this module summarizes trends and distributions that assist operational monitoring and management reporting.

Available reports include:

- Department-wise threat distribution.
- Role-based behavioural analysis.
- Alert severity distribution.
- Organizational threat statistics.
- Filtered alert exports.
- CSV report generation.

These reports support both operational decision-making and long-term behavioural trend analysis.

---

## 11.4 Dashboard Services

The presentation layer communicates with backend services through dedicated service modules responsible for database access and evidence generation.

These services provide:

- Database query abstraction.
- Behavioural evidence extraction.
- Historical baseline computation.
- Cohort comparison generation.
- Alert retrieval and updates.
- Cached analytical queries.

Separating dashboard logic from database operations improves maintainability while reducing duplication across interface components.

---

## 11.5 Visualization Components

Behavioural information is presented using interactive visualizations designed to improve analytical interpretation.

The dashboard includes graphical representations of:

- Behavioural timelines.
- Risk trends.
- Department distributions.
- Severity distributions.
- Comparative behavioural metrics.
- Historical activity summaries.

Visual representations allow analysts to identify behavioural trends significantly faster than manual inspection of tabular data alone.

---

## 11.6 Engineering Considerations

Several architectural decisions guided the implementation of the SOC Dashboard.

- The dashboard remains independent of the analytical pipeline and consumes processed data through service-layer interfaces.
- Cached database queries reduce repeated computation and improve responsiveness during investigations.
- Exception boundaries prevent individual dashboard failures from affecting the remainder of the application.
- Defensive input validation improves robustness against invalid user input.
- Behavioural evidence is generated dynamically to preserve explainability throughout the investigation process.
- Investigation workflows are integrated directly into the analyst interface, allowing behavioural analysis and operational response to occur within a single environment.

By combining alert management, forensic investigation, organizational reporting, and evidence-driven behavioural analysis within a unified interface, the SOC Dashboard transforms the outputs of the analytical pipeline into actionable cybersecurity intelligence suitable for operational insider threat investigations.

---

# 12. Validation, Verification & Security Hardening

Developing an analytical pipeline alone is insufficient for building a reliable cybersecurity platform. Beyond implementing behavioural analytics, Shatrubodh underwent a structured validation and hardening process to verify analytical correctness, improve operational robustness, strengthen repository security, and prepare the platform for demonstration and future extension.

The validation process focused on ensuring that each architectural layer behaved consistently under both expected and abnormal operating conditions while preserving the integrity of the behavioural analytics pipeline.

---

## 12.1 System Validation

Validation was performed across the complete end-to-end workflow, beginning with data ingestion and concluding with analyst investigations through the SOC dashboard.

The following components were verified during system validation:

- Data collection pipeline.
- Event normalization.
- SQLite database operations.
- Behaviour profile generation.
- Machine learning inference.
- Contextual risk assessment.
- Alert generation.
- Dashboard rendering.
- Reporting workflows.

Each stage was tested independently before validating the complete integrated pipeline.

---

## 12.2 Machine Learning Verification

Special attention was given to verifying the stability and reliability of the anomaly detection pipeline.

Verification activities included:

- Behaviour profile generation validation.
- Feature vector consistency checks.
- Isolation Forest inference validation.
- Local Outlier Factor (LOF) verification.
- Model serialization testing.
- Prediction reproducibility.
- Threshold verification.

Edge-case testing confirmed correct operation across varying behavioural profile sizes while ensuring analytical consistency throughout the pipeline.

---

## 12.3 Security Verification

Security verification focused on identifying implementation weaknesses that could compromise platform integrity.

The following assessments were performed:

- SQL injection review.
- Command execution review.
- Path traversal review.
- Cross-site scripting (XSS) review.
- Malformed input handling.
- JSON parsing validation.
- Defensive exception handling.

Parameterized SQL queries and layered service abstractions significantly reduced the attack surface associated with database operations.

No critical implementation vulnerabilities were identified during the security review.

---

## 12.4 Exception Boundary Hardening

Operational dashboards should remain available even when individual analytical components encounter unexpected conditions.

To improve system resilience, exception boundaries were introduced across dashboard services and analyst-facing modules.

Hardening included:

- Graceful database failure handling.
- Behavioural evidence fallback mechanisms.
- Dashboard rendering protection.
- Safe handling of missing records.
- Controlled degradation during service failures.
- Structured error reporting.

These improvements ensure that isolated failures do not propagate throughout the application.

---

## 12.5 Defensive Validation

Additional defensive programming techniques were incorporated to improve operational robustness.

Implemented safeguards include:

- Input validation.
- Type validation.
- Null-value protection.
- Safe numerical operations.
- Boundary condition handling.
- Invalid parameter rejection.
- Runtime assertions for critical operations.

These measures reduce unexpected runtime failures while improving long-term maintainability.

---

## 12.6 Performance Optimization

Several optimizations were introduced following validation to improve responsiveness without altering analytical behaviour.

Optimization measures include:

- Database indexing.
- Cached analytical queries.
- Query optimization.
- Reduced redundant database access.
- Optimized dashboard rendering.
- Efficient behavioural profile retrieval.

These improvements reduced investigation latency while preserving analytical correctness.

---

## 12.7 Repository & Environment Hardening

The repository was also reviewed to improve reproducibility and operational security.

Repository hardening included:

- Environment configuration cleanup.
- Dependency documentation.
- Repository hygiene improvements.
- Removal of obsolete tracked development artifacts.
- Expanded `.gitignore` protection.
- Protection of private development documentation.
- Verification that no hardcoded credentials or secrets were present within the source code.

These measures improve maintainability while reducing the risk of accidentally exposing development artifacts or sensitive information.

---

## 12.8 Validation Summary

The completed validation and hardening process demonstrated that Shatrubodh satisfies both its functional and engineering objectives.

The platform successfully provides:

- Stable end-to-end behavioural analytics.
- Reproducible machine learning inference.
- Explainable risk assessment.
- Reliable analyst investigation workflows.
- Robust exception handling.
- Defensive input validation.
- Repository security.
- Operational readiness for demonstration and further development.

While no software system can be considered entirely free of defects, the structured validation and production hardening process substantially improved the reliability, maintainability, and security posture of the platform, establishing a solid engineering foundation for future research and enterprise-scale enhancement.

---

# 13. Performance Evaluation

The performance of a User and Entity Behaviour Analytics (UEBA) platform extends beyond machine learning accuracy. Since Shatrubodh integrates data ingestion, behavioural analytics, contextual risk assessment, database operations, visualization, and analyst workflows into a unified system, overall performance depends upon the efficiency of each architectural layer as well as their interaction throughout the analytical pipeline.

Rather than evaluating isolated machine learning models, this chapter considers the operational performance of the complete platform following the validation and hardening activities described in the previous chapter.

---

## 13.1 End-to-End Pipeline Performance

The analytical workflow consists of multiple sequential stages:

1. Data ingestion.
2. Event normalization.
3. Behavioural profile generation.
4. Machine learning inference.
5. Contextual risk assessment.
6. Alert generation.
7. Dashboard visualization.

Validation confirmed that each stage executes successfully while preserving data consistency throughout the pipeline.

The modular separation between these stages minimizes processing dependencies and allows each component to be optimized independently without affecting the remainder of the system.

---

## 13.2 Database Performance

SQLite serves as the operational datastore for the platform.

To improve query performance, dedicated indexes were introduced for frequently accessed columns involved in dashboard rendering, behavioural lookups, historical investigations, and reporting workflows.

Additional optimizations include:

- Parameterized SQL queries.
- Query optimization.
- Reduced redundant database access.
- Cached analytical queries.
- Indexed alert retrieval.
- Optimized behavioural profile lookups.

These improvements significantly reduce database latency during analyst investigations while maintaining transactional consistency.

---

## 13.3 Analytics Performance

The behavioural analytics pipeline was designed to operate on engineered behavioural profiles rather than individual security events.

This design offers several computational advantages:

- Reduced feature dimensionality.
- Lower memory consumption.
- Faster model inference.
- Simplified statistical processing.
- Consistent feature representation.

By aggregating security telemetry into daily behavioural profiles before machine learning inference, computational complexity is substantially reduced compared with analysing raw event streams directly.

---

## 13.4 Dashboard Responsiveness

The Streamlit-based SOC Dashboard was optimized to provide responsive analyst interactions.

Performance improvements include:

- Cached database queries.
- Efficient data retrieval.
- Separation between service and presentation layers.
- Optimized chart generation.
- Reduced repeated computations.

These optimizations improve dashboard responsiveness during alert triage, threat hunting, and organizational reporting.

---

## 13.5 Scalability Considerations

Although Shatrubodh is implemented using SQLite for research and demonstration purposes, the modular architecture supports future scaling.

The following architectural decisions improve scalability:

- Independent processing layers.
- Modular data collectors.
- Separate analytics pipeline.
- Decoupled risk engine.
- Service-oriented dashboard architecture.
- Reusable behavioural profile generation.

These characteristics simplify future migration toward larger enterprise deployments without requiring significant architectural redesign.

---

## 13.6 Engineering Trade-offs

Several engineering trade-offs were intentionally made during development.

SQLite was selected because it provides portability, simplicity, and sufficient performance for research environments while avoiding unnecessary deployment complexity.

Behavioural aggregation was chosen instead of event-level machine learning to improve computational efficiency and analytical interpretability.

An unsupervised learning approach was adopted because labelled insider threat datasets are limited in real-world enterprise environments.

Finally, the separation of anomaly detection from contextual risk assessment improves explainability while reducing false-positive investigations.

---

## 13.7 Overall Evaluation

Validation and hardening demonstrated that Shatrubodh provides stable end-to-end execution across all implemented architectural layers.

The platform successfully combines:

- Efficient behavioural aggregation.
- Reproducible machine learning inference.
- Context-aware risk assessment.
- Responsive analyst workflows.
- Optimized database access.
- Reliable operational reporting.

Although developed as a research-oriented UEBA platform, the implemented architecture establishes a solid engineering foundation capable of supporting future enhancements such as distributed data collection, enterprise database backends, real-time event streaming, SIEM integration, and cloud-native deployment.

Overall, the completed implementation satisfies the intended design objectives while maintaining a balance between analytical capability, operational usability, maintainability, and computational efficiency.

---

# 14. Engineering Decisions & Design Rationale

The development of Shatrubodh was guided not only by functional requirements but also by a series of engineering decisions intended to maximize modularity, explainability, maintainability, and future extensibility. Rather than implementing isolated algorithms, the project was designed as a complete behavioural analytics platform in which each architectural component fulfills a clearly defined responsibility while remaining independent of adjacent layers.

This chapter discusses the major engineering decisions made throughout the development process and the rationale behind each choice.

---

## 14.1 Modular Layered Architecture

A layered architecture was adopted to separate the platform into independent functional components including data collection, normalization, feature engineering, behavioural analytics, contextual risk assessment, alert generation, database management, and visualization.

This separation provides several advantages:

- Improved maintainability.
- Independent module testing.
- Easier debugging.
- Clear separation of responsibilities.
- Simplified future feature additions.

Because each layer communicates through well-defined interfaces, modifications to one subsystem have minimal impact on the remainder of the platform.

---

## 14.2 Behavioural Analytics Instead of Rule-Based Detection

Traditional security monitoring frequently relies on manually maintained detection rules or predefined attack signatures.

Shatrubodh instead focuses on behavioural modelling.

Rather than attempting to identify known attacks, the platform establishes behavioural baselines and detects statistically significant deviations from normal user activity.

This approach allows previously unseen behavioural patterns to be identified without requiring continuously updated signature databases.

---

## 14.3 Daily Behavioural Profiling

Machine learning was intentionally applied to aggregated behavioural profiles rather than individual security events.

Daily aggregation was selected because it:

- Reduces computational complexity.
- Produces fixed-length feature vectors.
- Minimizes event-level noise.
- Preserves meaningful behavioural trends.
- Improves model stability.

This decision also simplifies analyst interpretation since investigations focus on behavioural summaries rather than thousands of individual log entries.

---

## 14.4 Ensemble Machine Learning

No single anomaly detection algorithm performs optimally across every behavioural scenario.

For this reason, Shatrubodh combines Isolation Forest and Local Outlier Factor into an ensemble analytical pipeline.

Isolation Forest identifies globally anomalous behaviour while Local Outlier Factor identifies localized deviations relative to neighbouring behavioural profiles.

Using both models provides a more balanced assessment than relying on either algorithm individually.

---

## 14.5 Separation of Analytics and Risk Assessment

One of the most important architectural decisions was separating statistical anomaly detection from operational risk assessment.

Machine learning models identify behavioural abnormalities.

The Risk Engine determines whether those abnormalities represent meaningful operational risk.

This separation improves:

- Explainability.
- Maintainability.
- Future extensibility.
- Analyst confidence.

It also allows contextual rules to evolve independently of the machine learning models.

---

## 14.6 Explainable Security Intelligence

Many anomaly detection systems produce numerical scores without sufficient justification.

Shatrubodh instead preserves behavioural evidence alongside every generated alert.

Analysts are provided with:

- Historical behavioural baselines.
- Peer cohort comparisons.
- Behavioural deviation metrics.
- Risk evidence.
- Timeline analysis.

This evidence-driven approach supports informed decision making rather than opaque machine learning outputs.

---

## 14.7 SQLite as the Operational Database

SQLite was selected as the database backend after considering the objectives of the project.

Its advantages include:

- Lightweight deployment.
- Zero configuration.
- ACID compliance.
- Portability.
- Sufficient performance for research and demonstration environments.

The modular storage layer also permits future migration to enterprise database systems with minimal architectural changes.

---

## 14.8 Service-Oriented Dashboard Design

The dashboard does not directly access database objects or analytical modules.

Instead, dedicated service modules perform:

- Database queries.
- Evidence generation.
- Historical analysis.
- Cohort comparisons.
- Alert retrieval.

This separation reduces code duplication while improving maintainability and testability.

---

## 14.9 Production Hardening

Engineering quality was treated as a core design objective rather than a post-development activity.

Structured validation and hardening introduced:

- Defensive input validation.
- Exception boundaries.
- Repository hardening.
- Database optimization.
- Query optimization.
- Secure parameterized SQL operations.
- Dependency documentation.

These improvements increased platform robustness without modifying analytical behaviour.

---

## 14.10 Extensibility

The platform was intentionally designed to support future enhancements.

Potential extensions include:

- Additional machine learning models.
- Live enterprise log ingestion.
- SIEM integration.
- REST APIs.
- Distributed databases.
- Containerized deployment.
- Threat intelligence integration.

Because the analytical pipeline is modular, these capabilities can be incorporated without requiring fundamental architectural redesign.

---

## 14.11 Summary

Every major engineering decision within Shatrubodh was made to balance analytical capability, operational usability, software maintainability, and future extensibility. Instead of developing a standalone anomaly detection model, the project evolved into a complete behavioural analytics platform that combines modular software engineering, explainable machine learning, contextual risk assessment, and analyst-centric investigation workflows. These design choices collectively establish a robust foundation for future research and enterprise-scale development.

---

# 15. Limitations

While Shatrubodh successfully implements a complete User and Entity Behaviour Analytics (UEBA) pipeline, it was developed as a research-oriented platform and therefore operates within several practical constraints. These limitations are acknowledged to provide an accurate understanding of the current implementation and to identify opportunities for future enhancement.

---

## 15.1 Dataset Dependency

The behavioural analytics pipeline was developed and evaluated using the CERT Insider Threat Dataset. Although the dataset provides realistic enterprise activity and simulated insider threat scenarios, it cannot fully capture the diversity and unpredictability of operational enterprise environments.

Consequently, behavioural patterns observed within production infrastructures may differ from those represented within the research dataset.

---

## 15.2 Batch Processing

The current implementation processes behavioural data in batches rather than continuously ingesting live enterprise events.

While this approach simplifies experimentation and model evaluation, production deployments would benefit from real-time event streaming and continuous behavioural analysis to reduce detection latency.

---

## 15.3 Limited Data Sources

The platform currently analyses authentication activity, endpoint events, file operations, removable media usage, email communications, and organizational directory information.

Modern enterprise security environments often generate additional telemetry from sources such as:

- Network traffic
- Cloud infrastructure
- Identity providers
- Endpoint Detection and Response (EDR) platforms
- Security Information and Event Management (SIEM) systems
- Threat intelligence platforms

Integrating these sources would improve behavioural visibility and contextual awareness.

---

## 15.4 Unsupervised Learning Constraints

Isolation Forest and Local Outlier Factor identify statistical deviations rather than malicious intent.

As a result:

- Not every anomaly represents an actual security incident.
- Legitimate operational changes may occasionally produce elevated anomaly scores.
- Analyst interpretation remains an essential component of the investigation process.

The contextual Risk Engine reduces this limitation but cannot eliminate it entirely.

---

## 15.5 Research-Scale Deployment

SQLite was selected because it provides a lightweight, portable, and reliable database suitable for research, demonstration, and educational environments.

Large enterprise deployments processing millions of daily events would likely require distributed database systems capable of supporting significantly higher ingestion rates and concurrent analytical workloads.

---

## 15.6 Static Risk Rules

The contextual Risk Engine currently applies predefined analytical rules to convert anomaly scores into operational risk.

Although this provides transparency and explainability, future implementations may benefit from adaptive or self-learning risk models capable of dynamically adjusting contextual weights based on organizational behaviour.

---

## 15.7 Platform Scope

Shatrubodh focuses specifically on insider threat detection through behavioural analytics.

It is not intended to replace comprehensive enterprise security platforms such as SIEM, SOAR, Endpoint Detection and Response (EDR), or Network Detection and Response (NDR) solutions. Instead, it should be viewed as a complementary behavioural intelligence component capable of integrating with broader cybersecurity ecosystems.

---

## 15.8 Summary

The identified limitations primarily reflect deliberate engineering trade-offs made to maintain architectural simplicity, explainability, and reproducibility within the scope of a research-oriented UEBA platform. None of these limitations affect the correctness of the implemented behavioural analytics pipeline; rather, they define clear directions for future development toward enterprise-scale deployment.

---

# 16. Future Work

Although Shatrubodh implements a complete User and Entity Behaviour Analytics (UEBA) pipeline, its modular architecture provides a strong foundation for future research and enterprise-scale enhancement. Several extensions can further improve analytical capability, scalability, automation, and operational effectiveness while preserving the existing architectural principles.

---

## 16.1 Real-Time Event Processing

The current implementation operates on behavioural data collected through a batch-processing workflow. Future versions can incorporate real-time event ingestion using message brokers and streaming frameworks to continuously update behavioural profiles and generate alerts with minimal latency.

Real-time processing would enable:

- Continuous behavioural monitoring.
- Near real-time anomaly detection.
- Faster incident response.
- Reduced detection latency.

---

## 16.2 Enterprise Log Integration

The modular collector architecture allows additional enterprise telemetry sources to be incorporated with minimal modification to the analytical pipeline.

Potential integrations include:

- Active Directory.
- Windows Event Logs.
- Sysmon.
- Microsoft Defender.
- Endpoint Detection and Response (EDR) platforms.
- Security Information and Event Management (SIEM) systems.
- Cloud identity providers.
- VPN authentication logs.
- Network flow data.

These integrations would significantly expand behavioural visibility across enterprise environments.

---

## 16.3 Advanced Machine Learning Models

While Isolation Forest and Local Outlier Factor provide effective unsupervised anomaly detection, future research may evaluate additional behavioural modelling approaches.

Potential analytical techniques include:

- Autoencoders.
- Variational Autoencoders (VAE).
- One-Class Support Vector Machines.
- Deep temporal sequence models.
- Graph Neural Networks.
- Transformer-based behavioural models.

Comparative evaluation of these approaches may further improve detection accuracy under different operational conditions.

---

## 16.4 Adaptive Risk Assessment

The current contextual Risk Engine applies predefined analytical rules to translate anomaly scores into operational risk.

Future implementations could introduce adaptive risk modelling capable of dynamically adjusting contextual weights based on organizational behaviour, historical investigations, analyst feedback, and evolving threat patterns.

Such adaptive scoring would improve prioritization while maintaining analytical transparency.

---

## 16.5 Threat Intelligence Integration

External cyber threat intelligence could be incorporated to enrich behavioural investigations.

Potential integrations include:

- MITRE ATT&CK mappings.
- STIX/TAXII threat feeds.
- Indicators of Compromise (IoCs).
- Organizational watchlists.
- Reputation services.

This additional context would improve investigative capabilities beyond behavioural analytics alone.

---

## 16.6 REST API and Automation

Providing a dedicated REST API would enable Shatrubodh to integrate with external security platforms and automated workflows.

Potential use cases include:

- SIEM integration.
- SOAR orchestration.
- Automated alert synchronization.
- Third-party dashboard integration.
- Programmatic behavioural queries.

API-driven architecture would significantly improve interoperability within enterprise security ecosystems.

---

## 16.7 Scalable Deployment

The current implementation utilizes SQLite because of its simplicity, portability, and suitability for research environments.

Future enterprise deployments may migrate toward:

- PostgreSQL.
- Distributed databases.
- Containerized microservices.
- Kubernetes orchestration.
- Cloud-native deployment architectures.

These enhancements would support significantly larger organizational environments while preserving the existing analytical pipeline.

---

## 16.8 Analyst Experience

Future improvements to the SOC Dashboard may include:

- Interactive investigation timelines.
- Case management workflows.
- Collaborative analyst workspaces.
- Alert correlation.
- Investigation templates.
- Executive reporting dashboards.

These enhancements would improve operational efficiency while reducing analyst workload.

---

## 16.9 Explainable Artificial Intelligence (XAI)

Future research may incorporate Explainable AI techniques to provide deeper insight into behavioural anomaly decisions.

Potential capabilities include:

- Feature contribution analysis.
- Model confidence estimation.
- Local explanation techniques.
- Interactive behavioural reasoning.
- Analyst-oriented decision visualization.

Improved explainability would strengthen analyst trust and support more informed investigation decisions.

---

## 16.10 Research Opportunities

The modular design of Shatrubodh enables future academic and industrial research across multiple cybersecurity domains, including:

- Insider threat detection.
- Behavioural analytics.
- User risk modelling.
- Security data engineering.
- Explainable machine learning.
- Human-centred cybersecurity.
- Security operations automation.

These research directions provide opportunities for extending the platform while maintaining compatibility with its existing architecture.

---

## 16.11 Summary

The architecture of Shatrubodh was intentionally designed with extensibility in mind. The platform can evolve beyond its current implementation through additional data sources, advanced machine learning models, adaptive risk assessment, enterprise integrations, scalable deployment strategies, and enhanced analyst workflows. These future enhancements would expand the platform's operational capabilities while preserving the modular engineering principles established throughout its development.

---

# 17. Conclusion

This report presented the complete design, development, implementation, and evaluation of **Shatrubodh**, a modular User and Entity Behaviour Analytics (UEBA) platform developed to address the problem of insider threat detection through behavioural analytics and unsupervised machine learning.

The project was undertaken in response to the Defence Research and Development Organisation (DRDO) problem statement titled **"User and Entity Behaviour Analytics (UEBA) for Internal Threat Identification."** Rather than implementing an isolated anomaly detection model, Shatrubodh evolved into a complete analytical platform encompassing data collection, event normalization, behavioural profile generation, anomaly detection, contextual risk assessment, alert generation, and an operational Security Operations Center (SOC) dashboard.

A modular software architecture was adopted throughout development to ensure clear separation between data ingestion, analytics, storage, and visualization layers. Behavioural profiles were engineered from normalized enterprise security events and analysed using an ensemble of Isolation Forest and Local Outlier Factor (LOF) models to identify statistically significant deviations from established behavioural baselines. These statistical outputs were subsequently enriched through a contextual Risk Engine, enabling anomaly scores to be translated into explainable operational risk assessments and actionable security alerts.

Beyond functional implementation, significant emphasis was placed on engineering quality. Structured validation, defensive programming, exception boundary hardening, repository hardening, database optimization, dependency management, and comprehensive documentation were incorporated to improve the reliability, maintainability, and reproducibility of the platform. These engineering efforts transformed the project from an analytical prototype into a production-hardened research platform suitable for demonstration, academic evaluation, and future enhancement.

Although the current implementation targets research and educational environments, the modular architecture provides a strong foundation for enterprise-scale expansion. The separation of functional responsibilities enables future integration with real-time data sources, additional behavioural models, enterprise security platforms, cloud-native deployments, and advanced threat intelligence without requiring fundamental architectural redesign.

Shatrubodh demonstrates that behavioural analytics, explainable machine learning, contextual risk modelling, and analyst-centric investigation workflows can be effectively integrated into a unified UEBA platform capable of supporting insider threat detection in modern enterprise environments. More importantly, the project highlights the value of combining sound software engineering principles with practical cybersecurity techniques to develop systems that are not only functionally effective but also maintainable, extensible, and operationally relevant.

The completed platform represents both a practical implementation of the DRDO problem statement and a strong foundation for continued research in behavioural cybersecurity, insider threat detection, and intelligent security operations.

---

# 18. References

[1] Defence Research and Development Organisation (DRDO), *User and Entity Behaviour Analytics (UEBA) for Internal Threat Identification*, Ministry of Defence, Government of India.

[2] CERT Program, Carnegie Mellon University, *CERT Insider Threat Dataset*, Carnegie Mellon University.

[3] Mrajaxnp, *CERT Insider Threat Detection Research Dataset (Kaggle Mirror)*, Kaggle. Available: https://www.kaggle.com/datasets/mrajaxnp/cert-insider-threat-detection-research/

[4] F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," *Proceedings of the 8th IEEE International Conference on Data Mining (ICDM)*, Pisa, Italy, 2008, pp. 413–422.

[5] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, "LOF: Identifying Density-Based Local Outliers," *Proceedings of the ACM SIGMOD International Conference on Management of Data*, Dallas, Texas, USA, 2000, pp. 93–104.

[6] Pedregosa, F., Varoquaux, G., Gramfort, A., et al., "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.

[7] The scikit-learn Developers, *Scikit-learn Documentation*. Available: https://scikit-learn.org/

[8] The Pandas Development Team, *Pandas Documentation*. Available: https://pandas.pydata.org/

[9] Harris, C. R., Millman, K. J., van der Walt, S. J., et al., "Array Programming with NumPy," *Nature*, vol. 585, pp. 357–362, 2020.

[10] The Streamlit Team, *Streamlit Documentation*. Available: https://streamlit.io/

[11] SQLite Consortium, *SQLite Documentation*. Available: https://www.sqlite.org/

[12] Joblib Development Team, *Joblib Documentation*. Available: https://joblib.readthedocs.io/

---

# Appendix A – Project Statistics

The following statistics summarize the final implementation state of the Shatrubodh platform at the time of completion.

| Category | Value |
|----------|------:|
| Stable Version | v0.10.5 |
| Final Stable Phase | Phase 10 – Production Hardening |
| Active Python Source Files | 17 |
| Total Python Files (including `__init__.py`) | 21 |
| Approximate Python LOC | ~2,700 |
| Active Source Directories | 10 |
| Database Backend | SQLite |
| Database Tables | 6 |
| SQL Indexes | 10 |
| Behavioural Metrics | 14 |
| Machine Learning Models | 2 |
| Dashboard Modules | 3 |
| Alert Severity Levels | 3 |
| Investigation States | 4 |
| Primary Dataset | CERT Insider Threat Dataset |
| Development Language | Python |
| Frontend Framework | Streamlit |
| Machine Learning Library | Scikit-learn |
| Data Processing Libraries | Pandas, NumPy |
| Model Serialization | Joblib |

## Functional Modules

The completed platform consists of the following primary functional modules:

- Data Collection
- Event Normalization
- SQLite Storage
- Behaviour Profile Generation
- Anomaly Detection
- Contextual Risk Engine
- Alert Generation
- SOC Dashboard
- Threat Hunter
- Organizational Reporting

## Final Repository Status

- Modular layered architecture.
- End-to-end behavioural analytics pipeline.
- Production hardening completed.
- Repository hardening completed.
- Defensive validation implemented.
- Exception boundary protection implemented.
- Parameterized SQL throughout.
- Indexed database schema.
- Dependency documentation completed.
- Repository documentation completed.

The implementation presented in this report corresponds to the final production-hardened state of the Shatrubodh project after completion of all development, validation, documentation, and repository hardening activities.