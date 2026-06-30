# src/dashboard/pages/threat_hunter.py

import streamlit as st
import pandas as pd
from dashboard.services.db_service import (
    get_connection,
    get_user_demographics,
    get_user_rolling_history,
    get_cohort_population_history,
    get_user_risk_timeline
)
from dashboard.services.evidence_parser import parse_evidence, compute_comparisons, METRICS_COLUMNS
from dashboard.components.charts import plot_risk_timeline, plot_metric_comparison

def get_user_alerts(user_id: str) -> pd.DataFrame:
    """
    Queries all alerts associated with a specific user.
    """
    conn = get_connection()
    query = """
        SELECT alert_id, alert_date, severity, status, reasons, evidence_json, analyst_notes
        FROM alerts
        WHERE user_id = ?
        ORDER BY alert_date DESC
    """
    df = pd.read_sql_query(query, conn, params=[user_id])
    conn.close()
    return df

def get_user_behavior_history(user_id: str) -> pd.DataFrame:
    """
    Queries recent behavior profiles for a user.
    """
    conn = get_connection()
    query = """
        SELECT profile_date, logon_count, usb_insertions, file_copy_to_usb, email_exfil_bytes, unique_pcs, total_events
        FROM behavior_profiles
        WHERE user_id = ?
        ORDER BY profile_date DESC
        LIMIT 50
    """
    df = pd.read_sql_query(query, conn, params=[user_id])
    conn.close()
    return df

def render_threat_hunter():
    """
    Renders the Threat Hunter tab for forensic deep dive investigations.
    """
    st.subheader("Forensic Deep Dive")
    
    # 1. User Search
    user_id = st.text_input("Search Analyst Workstation (Enter User ID)", value="", key="th_user_search").strip()
    
    if not user_id:
        st.info("Enter a User ID in the field above to start the threat hunting investigation.")
        return
        
    # 2. Get demographics
    demographics = get_user_demographics(user_id)
    if not demographics:
        st.error(f"User '{user_id}' not found in the identity system database.")
        return
        
    # 3. User Demographics Panel
    st.markdown("### Identity Demographics")
    st.write(
        f"**Name**: {demographics['name']} | "
        f"**Department**: {demographics['department']} | "
        f"**Role**: {demographics['role']} | "
        f"**Manager**: {demographics['manager']} | "
        f"**Team**: {demographics['team']}"
    )
    
    st.markdown("---")
    
    # 4. Alert Selection
    df_alerts = get_user_alerts(user_id)
    if df_alerts.empty:
        st.warning(f"No threat alerts recorded for user '{user_id}'. Threat hunter deep-dive requires an alert context.")
        return
        
    alert_options = df_alerts['alert_id'].tolist()
    alert_map = df_alerts.set_index('alert_id').to_dict('index')
    
    def format_alert_choice(aid):
        item = alert_map[aid]
        return f"ID: {aid} | Date: {item['alert_date']} | Sev: {item['severity']} | Status: {item['status']}"
        
    selected_alert_id = st.selectbox(
        "Select Investigation Alert Context",
        options=alert_options,
        format_func=format_alert_choice,
        key="th_selected_alert"
    )
    
    if selected_alert_id:
        render_investigation_view(user_id, demographics, alert_map[selected_alert_id], selected_alert_id)

def render_investigation_view(user_id: str, demographics: dict, alert_data: dict, alert_id: str):
    """
    Renders the full forensic analysis of the selected alert context.
    """
    alert_date = alert_data['alert_date']
    dept = demographics['department']
    role = demographics['role']
    
    # Fetch histories
    user_history = get_user_rolling_history(user_id, alert_date)
    cohort_history = get_cohort_population_history(dept, role, alert_date)
    
    # 1. Low history profile warning
    if len(user_history) < 30:
        st.warning(
            f"Low history profile count: User only has {len(user_history)} days of baseline data prior to the alert date "
            f"(expected 30 days). Standard deviations and Z-scores may be volatile."
        )
        
    # 2. Parse evidence and compute deviations
    alert_evidence = parse_evidence(alert_data['evidence_json'])
    df_comparisons = compute_comparisons(alert_evidence, user_history, cohort_history)
    
    st.markdown("### Evidence Breakdown & Deviation Analysis")
    st.markdown(f"**Selected Alert Context**: `{alert_id}` | **Trigger Date**: `{alert_date}`")
    st.markdown(f"**Reasons**: *{alert_data['reasons']}*")
    
    st.dataframe(df_comparisons, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 3. Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Risk Timeline")
        df_timeline = get_user_risk_timeline(user_id)
        plot_risk_timeline(df_timeline)
        
    with col2:
        st.markdown("### Comparative Baseline Visual")
        
        # User select metric to plot
        display_metrics = [m.replace('_', ' ').title() for m in METRICS_COLUMNS]
        selected_metric_title = st.selectbox(
            "Compare Metric Baseline",
            options=display_metrics,
            key="th_compare_metric_select"
        )
        
        # Resolve metrics
        metric_idx = display_metrics.index(selected_metric_title)
        db_col = METRICS_COLUMNS[metric_idx]
        
        # Calculate raw values for plotting
        alert_val = float(alert_evidence.get(db_col, 0.0))
        
        df_user = pd.DataFrame(user_history, columns=METRICS_COLUMNS) if user_history else pd.DataFrame()
        df_cohort = pd.DataFrame(cohort_history, columns=METRICS_COLUMNS) if cohort_history else pd.DataFrame()
        
        user_mean = float(df_user[db_col].mean()) if not df_user.empty else 0.0
        cohort_mean = float(df_cohort[db_col].mean()) if not df_cohort.empty else 0.0
        
        # email exfil in MB
        if db_col == 'email_exfil_bytes':
            alert_val /= (1024 * 1024)
            user_mean /= (1024 * 1024)
            cohort_mean /= (1024 * 1024)
            label = f"{selected_metric_title} (MB)"
        else:
            label = selected_metric_title
            
        plot_metric_comparison(label, alert_val, user_mean, cohort_mean)
        
    st.markdown("---")
    
    # 4. User Behavior History Table
    st.markdown("### Historical Daily Behavior Profiles (Most Recent)")
    df_beh_history = get_user_behavior_history(user_id)
    if not df_beh_history.empty:
        # Format exfil bytes to MB
        df_beh_history_display = df_beh_history.copy()
        df_beh_history_display['email_exfil_bytes'] = df_beh_history_display['email_exfil_bytes'] / (1024 * 1024)
        df_beh_history_display.columns = [
            'Date', 'Logons', 'USB Inserts', 'USB Copy Count', 'Email Exfil (MB)', 'PCs Used', 'Total Events'
        ]
        st.dataframe(df_beh_history_display, use_container_width=True, hide_index=True)
    else:
        st.info("No daily behavior profiles recorded for this user.")
