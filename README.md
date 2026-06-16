# Shatrubodh

AI-driven User and Entity Behavior Analytics (UEBA) for internal threat detection.

## Overview
Shatrubodh is a security intelligence platform that uses unsupervised machine learning to baseline normal user behavior and flag anomalies. By analyzing system logs, it helps security teams identify potential insider threats before they escalate.

## Key Features
- **Behavioral Baselining:** Uses Isolation Forest to learn patterns of normal activity.
- **Real-time Monitoring:** Interactive Streamlit dashboard with live alert feeds.
- **AI Explanations:** Get context on why a specific event was flagged as anomalous.
- **Threat Hunting:** Deep dive into user-specific risk scores and historical activity.
- **Customizable Alerts:** Adjustable risk thresholds and alert management (Confirm/False Positive).
- **Data Simulation:** Built-in generator for creating realistic synthetic security logs.

## Technology Stack
- **Python 3.x**
- **Streamlit** (UI Framework)
- **Scikit-learn** (Machine Learning)
- **Pandas/NumPy** (Data Processing)
- **Joblib** (Model Persistence)
- **Faker** (Data Generation)

## Project Structure
```text
Shatrubodh/
├── src/
│   ├── app.py                # Streamlit UI & Main Logic
│   ├── anomaly_detector.py   # Isolation Forest Implementation
│   ├── data_generator.py     # Synthetic Log Generation
│   ├── utils.py              # Data Preprocessing & Feature Engineering
│   └── model.pkl             # Trained Model (Auto-generated)
├── project_report.txt        # Detailed project overview
└── README.md                 # Project documentation
```

## Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/utkarshhh0/Shatrubodh.git
   cd Shatrubodh
   ```
2. Install dependencies:
   ```bash
   pip install streamlit pandas scikit-learn joblib faker
   ```

### Running the Application
```bash
streamlit run src/app.py
```

## How it Works
1. **Data Prep:** The system processes logs, extracting features like `action_type`, `bytes_transferred`, and `timestamp` (converted to hour/day).
2. **Training:** An Isolation Forest model is trained on the data to identify the "norm".
3. **Detection:** New events are scored. Events that fall into isolated regions of the feature space receive higher risk scores.
4. **Visualization:** Anomalies are presented in the dashboard for investigator review.

## Contributors
- **Utkarsh Gupta**

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
