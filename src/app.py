import streamlit as st
import pandas as pd
import os
import sys

from data_generator import generate_mock_data
from anomaly_detector import AnomalyDetector

st.set_page_config(page_title="Shatrubodh", layout="wide",
                   initial_sidebar_state="expanded")


def load_css():
    st.markdown("""
        <style>
        body {
            font-family: 'Fira Mono', 'Roboto Mono', 'Courier New', monospace;
        }

        .glass-container {
            background: rgba(127, 60, 255, 0.1); /* Semi-transparent purple */
            border-radius: 16px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px); /* Blur effect */
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(127, 60, 255, 0.3); /* Soft purple edge */
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }

        .main-title {
            font-family: 'Fira Mono', 'Roboto Mono', 'Courier New', monospace;
            font-size: 6em; /* Increased size */
            font-weight: bold;
            color: #ffffff; /* White text for contrast */
            text-shadow: 0 0 10px #7f3cff,
                         0 0 20px #7f3cff,
                         0 0 30px #7f3cff,
                         0 0 40px #7f3cff;
            margin-bottom: 0.1em;
        }

        .subtitle {
            font-family: 'Fira Mono', 'Roboto Mono', 'Courier New', monospace;
            font-size: 0.9em; /* Very small */
            color: #a070ff; /* Lighter purple accent */
            text-shadow: 0 0 5px rgba(160, 112, 255, 0.5); /* Gentle shadow */
            margin-top: 0;
        }
        </style>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
        ---
        <p style="text-align: center; color: grey;">
            <strong>Shatrubodh: Insider Threat Intelligence Platform</strong> |
            Developed for Team Balidan |
            &copy; 2025 Utkarsh Gupta, Deepak Singh Rawat |
            <a href="mailto:deepu2005rawat@gmail.com" style="color: grey;">Contact Us</a> |
            <a href="https://github.com/utkarshhh0/Shatrubodh" style="color: grey;">Help</a>
        </p>
    """, unsafe_allow_html=True)


def main():
    load_css()
    st.markdown("""
        <div class="glass-container">
            <h1 class="main-title">SHATRUBODH</h1>
            <p class="subtitle">user and entity behavior analysis (UEBA) for internal threat</p>
        </div>
    """, unsafe_allow_html=True)
    st.caption(f"Synthetic data loaded for demo purposes. Last updated: "
               f"{pd.to_datetime('now')}")

    with st.sidebar:
        st.header("System Controls")
        uploaded_file = st.file_uploader("Upload Log File", type=["csv"])
        alert_threshold = st.slider("Alert Risk Threshold", 0, 100, 70)
        if st.button("Retrain Model"):
            train_model(uploaded_file)

    df = load_data(uploaded_file)
    if not os.path.exists("src/model.pkl"):
        train_model(uploaded_file)

    detector = AnomalyDetector()
    # Explicitly get results and merge them
    risk_scores, is_anomaly = detector.predict(df)
    results_df = df.copy()
    results_df['risk_score'] = risk_scores
    results_df['is_anomaly'] = is_anomaly

    user_risk = results_df.groupby('user_id')['risk_score'].mean().reset_index()
    alerts = results_df[results_df['risk_score'] > alert_threshold].sort_values(
        'timestamp', ascending=False)

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Threat Hunter", "System & Reports"])

    with tab1:
        render_dashboard(results_df, alerts)
    with tab2:
        render_threat_hunter(results_df, user_risk)
    with tab3:
        render_system_reports(alerts)

    render_footer()


def train_model(uploaded_file):
    with st.spinner("Training model..."):
        detector = AnomalyDetector()
        detector.train(load_data(uploaded_file))
    st.success("Model trained.")


def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file if uploaded_file else "src/sample_data.csv")
    except FileNotFoundError:
        generate_mock_data()
        df = pd.read_csv("src/sample_data.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def render_dashboard(df, alerts):
    st.subheader("Live Alert Feed")
    for _, alert in alerts.head().iterrows():
        with st.expander(f":warning: High-Risk Activity by **{alert['user_id']}** "
                           f"at {alert['timestamp']}"):
            st.write(alert.to_dict())
            if st.button(f"Get AI Explanation##{alert.name}", key=f"exp_{alert.name}"):
                st.info(f"**AI Analysis:** This event is flagged as anomalous because "
                        f"the action **'{alert['action_type']}'** with a data transfer of "
                        f"**{alert['bytes_transferred']} bytes** deviates significantly "
                        f"from the user's established behavioral baseline.")

    st.subheader("Special Activity Monitoring")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Recent USB Usage**")
        st.dataframe(df[df['usb_device'] != 'N/A'].tail(),
                     use_container_width=True)
    with c2:
        st.write("**Recent Large File Transfers**")
        st.dataframe(df[df['bytes_transferred'] > 1024 * 1024 * 10].tail(),
                     use_container_width=True)


def render_threat_hunter(df, user_risk):
    st.subheader("User Risk Profiles")
    selected_user = st.selectbox("Select a user", user_risk['user_id'])
    st.dataframe(user_risk.sort_values('risk_score', ascending=False),
                 use_container_width=True)

    st.subheader(f"Activity for {selected_user}")
    user_activity = df[df['user_id'] == selected_user]
    st.dataframe(user_activity, use_container_width=True)


def render_system_reports(alerts):
    st.subheader("Alert Feedback & Reporting")
    if not alerts.empty:
        selected_alert_idx = st.selectbox("Select an alert to review",
                                          alerts.index)
        alert_data = alerts.loc[selected_alert_idx]
        st.json(alert_data.to_json())

        c1, c2, c3 = st.columns(3)
        if c1.button("Mark as False Positive"):
            st.success(f"Alert {selected_alert_idx} marked as False Positive.")
        if c2.button("Confirm Threat"):
            st.warning(f"Alert {selected_alert_idx} confirmed as a threat.")
        if c3.button("Mark for Investigation"):
            st.info(f"Alert {selected_alert_idx} marked for further investigation.")

    st.subheader("Export Alerts & Reports")

    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        min_date = alerts['timestamp'].min().date() if not alerts.empty \
            else pd.to_datetime('today').date()
        max_date = alerts['timestamp'].max().date() if not alerts.empty \
            else pd.to_datetime('today').date()
        date_range = st.date_input("Date Range", value=(min_date, max_date),
                                   key="export_date_range")

        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            # Default to min/max if only one date selected
            start_date, end_date = min_date, max_date

    with col2:
        all_users = alerts['user_id'].unique().tolist() if not alerts.empty \
            else []
        selected_users = st.multiselect("Filter by User", options=all_users,
                                        default=all_users, key="export_users")

    min_risk = alerts['risk_score'].min() if not alerts.empty else 0
    max_risk = alerts['risk_score'].max() if not alerts.empty else 100
    risk_threshold_range = st.slider("Filter by Risk Score", 0, 100,
                                     (int(min_risk), int(max_risk)),
                                     key="export_risk_range")

    alert_status_options = ["All", "Anomaly", "Normal"]
    selected_status = st.selectbox("Filter by Alert Status",
                                   options=alert_status_options, index=0,
                                   key="export_status")

    # Apply filters
    filtered_alerts = alerts.copy()

    if not alerts.empty:
        # Date range filter
        filtered_alerts = filtered_alerts[
            (filtered_alerts['timestamp'].dt.date >= start_date) &
            (filtered_alerts['timestamp'].dt.date <= end_date)
        ]

        # User filter
        if selected_users:
            filtered_alerts = filtered_alerts[
                filtered_alerts['user_id'].isin(selected_users)]

        # Risk score filter
        filtered_alerts = filtered_alerts[
            (filtered_alerts['risk_score'] >= risk_threshold_range[0]) &
            (filtered_alerts['risk_score'] <= risk_threshold_range[1])
        ]

        # Alert status filter
        if selected_status == "Anomaly":
            filtered_alerts = filtered_alerts[filtered_alerts['is_anomaly'] == 1]
        elif selected_status == "Normal":
            filtered_alerts = filtered_alerts[filtered_alerts['is_anomaly'] == -1]

    st.write(f"Filtered Alerts: {len(filtered_alerts)} records")

    # Download button
    if not filtered_alerts.empty:
        csv = filtered_alerts.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Alerts as CSV",
            data=csv,
            file_name="shatrubodh_alerts.csv",
            mime="text/csv",
            key="download_alerts_csv"
        )
    else:
        st.info("No alerts match the current filters.")


if __name__ == "__main__":
    main()