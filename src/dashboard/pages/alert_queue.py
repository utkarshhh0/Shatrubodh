# src/dashboard/pages/alert_queue.py

import streamlit as st
import pandas as pd
from dashboard.services.db_service import get_alert_counts, get_alert_queue, update_alert_status
from dashboard.services.evidence_parser import parse_evidence

def render_alert_queue():
    """
    Renders the Dashboard/Alert Queue tab: triage feed, status/severity filters,
    user search, detail panel, and analyst feedback actions.
    """
    st.subheader("Alert Triage Feed")
    
    # 1. Compact Analyst-Oriented Statistics
    counts = get_alert_counts()
    st.write(
        f"**Alerts Summary** | "
        f"Critical: `{counts.get('critical', 0)}` | "
        f"High: `{counts.get('high', 0)}` | "
        f"Medium: `{counts.get('medium', 0)}` || "
        f"New: `{counts.get('new', 0)}` | "
        f"Investigating: `{counts.get('in_progress', 0)}`"
    )
    
    st.markdown("---")
    
    # 2. Filters Grid
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filters = st.multiselect(
            "Status Filter",
            options=['New', 'In_Progress', 'Resolved', 'False_Positive'],
            default=['New', 'In_Progress'],
            key="aq_status_filter"
        )
    with col2:
        severity_filters = st.multiselect(
            "Severity Filter",
            options=['Critical', 'High', 'Medium'],
            default=['Critical', 'High', 'Medium'],
            key="aq_severity_filter"
        )
    with col3:
        user_id_search = st.text_input(
            "Search User ID",
            value="",
            key="aq_user_search"
        )
        
    # Date filters (optional, but supported in db_service)
    # Let's keep it simple and default to no date range restriction unless specified
    
    # 3. Query Alerts
    # Limit alerts to 100 for the feed to keep it responsive
    df_alerts = get_alert_queue(
        status_filters=status_filters if status_filters else None,
        severity_filters=severity_filters if severity_filters else None,
        user_id_search=user_id_search.strip() if user_id_search else "",
        limit=100
    )
    
    if df_alerts.empty:
        st.info("No alerts found matching the active filters.")
        return
        
    # 4. Display Alert Table
    # Clean display columns
    display_df = df_alerts[[
        'alert_id', 'user_id', 'alert_date', 'severity', 'status', 'risk_score', 'assigned_to'
    ]].copy()
    display_df.columns = ['Alert ID', 'User ID', 'Alert Date', 'Severity', 'Status', 'Risk Score', 'Assigned To']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 5. Alert Selection for Investigation/Feedback
    alert_options = df_alerts['alert_id'].tolist()
    
    # Create format mapping for selectbox options
    alert_map = df_alerts.set_index('alert_id').to_dict('index')
    
    def format_alert_option(aid):
        item = alert_map[aid]
        return f"{item['user_id']} | {item['alert_date']} | {item['severity']} | Risk: {item['risk_score']:.1f} ({item['status']})"
        
    selected_alert_id = st.selectbox(
        "Select Alert to Triage",
        options=alert_options,
        format_func=format_alert_option,
        key="aq_selected_alert_id"
    )
    
    if selected_alert_id:
        st.markdown("---")
        render_alert_detail_panel(alert_map[selected_alert_id], selected_alert_id)

def render_alert_detail_panel(alert_data: dict, alert_id: str):
    """
    Renders detail panel and action form for a selected alert.
    """
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Alert Details")
        st.markdown(f"**Alert ID**: `{alert_id}`")
        st.markdown(f"**Target User**: `{alert_data['user_id']}`")
        st.markdown(f"**Occurrence Date**: `{alert_data['alert_date']}`")
        st.markdown(f"**Risk Score**: `{alert_data['risk_score']:.2f}`")
        st.markdown(f"**Severity**: `{alert_data['severity']}`")
        st.markdown(f"**Assigned Analyst**: `{alert_data['assigned_to'] or 'Unassigned'}`")
        st.markdown(f"**Reason for Alert**:")
        st.write(alert_data['reasons'])
        
        # Parse and display evidence
        evidence = parse_evidence(alert_data['evidence_json'])
        if evidence:
            st.markdown("**Evidence Metrics**:")
            # Exclude metadata columns
            display_evidence = {
                k.replace('_', ' ').title(): v 
                for k, v in evidence.items() 
                if k not in ['profile_id', 'user_id', 'profile_date', 'department', 'role']
            }
            st.json(display_evidence)
            
    with col2:
        st.markdown("### Analyst Action Board")
        
        current_status = alert_data['status']
        status_options = ['New', 'In_Progress', 'Resolved', 'False_Positive']
        try:
            status_index = status_options.index(current_status)
        except ValueError:
            status_index = 0
            
        new_status = st.selectbox(
            "Triage Status",
            options=status_options,
            index=status_index,
            key="aq_new_status"
        )
        
        new_assignee = st.text_input(
            "Assignee Name",
            value=alert_data['assigned_to'] or "",
            key="aq_new_assignee"
        )
        
        new_notes = st.text_area(
            "Analyst Notes",
            value=alert_data['analyst_notes'] or "",
            height=150,
            key="aq_new_notes"
        )
        
        if st.button("Commit Action", key="aq_commit_btn"):
            update_alert_status(
                alert_id=alert_id,
                status=new_status,
                assigned_to=new_assignee.strip() if new_assignee else None,
                analyst_notes=new_notes.strip() if new_notes else None
            )
            st.success("Triage update successfully committed to database!")
            st.rerun()
