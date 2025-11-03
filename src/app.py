import streamlit as st
import pandas as pd
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_generator import generate_mock_data
from src.anomaly_detector import AnomalyDetector

st.set_page_config(page_title="Shatrubodh", layout="wide", initial_sidebar_state="expanded")

def load_css():
    st.markdown("<style>/* CSS content from previous steps */</style>", unsafe_allow_html=True)

def main():
    load_css()
    st.title("⚔️ Shatrubodh: Insider Threat Intelligence Platform")
    st.caption(f"Synthetic data loaded for demo purposes. Last updated: {pd.to_datetime('now')}")

    with st.sidebar:
        st.header("System Controls")
        uploaded_file = st.file_uploader("Upload Log File", type=["csv"])
        alert_threshold = st.slider("Alert Risk Threshold", 0, 100, 70)
        if st.button("Retrain Model"):
            train_model(uploaded_file)

    df = load_data(uploaded_file)
    if not os.path.exists("src/model.pkl"): train_model(uploaded_file)
    
    detector = AnomalyDetector()
    # Explicitly get results and merge them
    risk_scores, is_anomaly = detector.predict(df)
    results_df = df.copy()
    results_df['risk_score'] = risk_scores
    results_df['is_anomaly'] = is_anomaly

    user_risk = results_df.groupby('user_id')['risk_score'].mean().reset_index()
    alerts = results_df[results_df['risk_score'] > alert_threshold].sort_values('timestamp', ascending=False)

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Threat Hunter", "System & Reports"])
    
    with tab1:
        render_dashboard(results_df, alerts)
    with tab2:
        render_threat_hunter(results_df, user_risk)
    with tab3:
        render_system_reports(alerts)

def train_model(uploaded_file):
    with st.spinner("Training model..."): detector = AnomalyDetector(); detector.train(load_data(uploaded_file))
    st.success("Model trained.")

def load_data(uploaded_file):
    try: df = pd.read_csv(uploaded_file if uploaded_file else "src/sample_data.csv")
    except FileNotFoundError: generate_mock_data(); df = pd.read_csv("src/sample_data.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def render_dashboard(df, alerts):
    st.subheader("Live Alert Feed")
    for _, alert in alerts.head().iterrows():
        with st.expander(f":warning: High-Risk Activity by **{alert['user_id']}** at {alert['timestamp']}"):
            st.write(alert.to_dict())
            if st.button(f"Get AI Explanation##{alert.name}", key=f"exp_{alert.name}"):
                st.info(f"**AI Analysis:** This event is flagged as anomalous because the action **'{alert['action_type']}'** with a data transfer of **{alert['bytes_transferred']} bytes** deviates significantly from the user's established behavioral baseline.")

    st.subheader("Special Activity Monitoring")
    c1, c2 = st.columns(2)
    with c1: st.write("**Recent USB Usage**"); st.dataframe(df[df['usb_device']!='N/A'].tail(), use_container_width=True)
    with c2: st.write("**Recent Large File Transfers**"); st.dataframe(df[df['bytes_transferred'] > 1024*1024*10].tail(), use_container_width=True)

def render_threat_hunter(df, user_risk):
    st.subheader("User Risk Profiles")
    selected_user = st.selectbox("Select a user", user_risk['user_id'])
    st.dataframe(user_risk.sort_values('risk_score', ascending=False), use_container_width=True)
    
    st.subheader(f"Activity for {selected_user}")
    user_activity = df[df['user_id'] == selected_user]
    st.dataframe(user_activity, use_container_width=True)

def render_system_reports(alerts):
    st.subheader("Alert Feedback & Reporting")
    if not alerts.empty:
        selected_alert_idx = st.selectbox("Select an alert to review", alerts.index)
        alert_data = alerts.loc[selected_alert_idx]
        st.json(alert_data.to_json())

        c1, c2, c3 = st.columns(3)
        if c1.button("Mark as False Positive"):
            st.success(f"Alert {selected_alert_idx} marked as False Positive.")
        if c2.button("Confirm Threat"):
            st.warning(f"Alert {selected_alert_idx} confirmed as a threat.")
        if c3.button("Mark for Investigation"):
            st.info(f"Alert {selected_alert_idx} marked for further investigation.")
    
    st.subheader("Future Enhancements")
    st.markdown("- **Model Retraining:** Integrate feedback to periodically retrain the IsolationForest model.\n- **Real-time Data Ingestion:** Connect to a live data stream (e.g., Kafka, Splunk) instead of CSV uploads.\n- **Role-Based Access Control:** Implement user roles for analysts and administrators.\n- **Advanced Visualization:** Use 3D graphs to correlate more data dimensions.")

if __name__ == "__main__":
    main()