# src/dashboard/pages/reports.py

import streamlit as st
import pandas as pd
from dashboard.services.db_service import (
    get_department_threat_density,
    get_role_threat_density,
    get_alert_queue
)
from dashboard.components.charts import plot_department_distribution

def render_reports():
    """
    Renders the System & Reports page containing department/role alert tables,
    distribution charts, and CSV exporting tools.
    """
    st.subheader("System Metrics & Reports")
    
    # 1. Department threat distribution
    st.markdown("### Department Threat Distribution")
    try:
        df_dept = get_department_threat_density()
    except Exception as e:
        st.error("Unable to load component.")
        st.exception(e)
        df_dept = pd.DataFrame()
        
    if not df_dept.empty:
        try:
            # Plot distribution using simple native chart
            plot_department_distribution(df_dept)
            
            # Display department summary table
            dept_table = df_dept.rename(columns={
                'department': 'Department',
                'alert_count': 'Total Alerts',
                'critical_count': 'Critical',
                'high_count': 'High',
                'medium_count': 'Medium'
            })
            st.dataframe(dept_table, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error("Unable to load component.")
            st.exception(e)
    else:
        st.info("No department threat statistics found.")
        
    st.markdown("---")
    
    # 2. Top Anomalous Roles Table
    st.markdown("### Role Threat Distribution (Top 10 Anomalous Roles)")
    try:
        df_role = get_role_threat_density()
    except Exception as e:
        st.error("Unable to load component.")
        st.exception(e)
        df_role = pd.DataFrame()
        
    if not df_role.empty:
        try:
            role_table = df_role.rename(columns={
                'role': 'Employee Role',
                'alert_count': 'Alert Count'
            })
            st.dataframe(role_table, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error("Unable to load component.")
            st.exception(e)
    else:
        st.info("No role threat statistics found.")
        
    st.markdown("---")
    
    # 3. CSV Export Section
    st.markdown("### Export Alerts Database")
    
    col1, col2 = st.columns(2)
    with col1:
        export_status = st.multiselect(
            "Filter by Status (Export)",
            options=['New', 'In_Progress', 'Resolved', 'False_Positive'],
            default=['New', 'In_Progress', 'Resolved', 'False_Positive'],
            key="rep_export_status"
        )
        export_user = st.text_input(
            "Filter by User ID (Export)",
            value="",
            key="rep_export_user"
        )
    with col2:
        export_severity = st.multiselect(
            "Filter by Severity (Export)",
            options=['Critical', 'High', 'Medium'],
            default=['Critical', 'High', 'Medium'],
            key="rep_export_severity"
        )
        export_limit = st.number_input(
            "Export Limit Count",
            min_value=1,
            max_value=10000,
            value=1000,
            key="rep_export_limit"
        )
        
    if st.button("Query Export Queue", key="rep_query_export_btn"):
        try:
            df_export = get_alert_queue(
                status_filters=export_status if export_status else None,
                severity_filters=export_severity if export_severity else None,
                user_id_search=export_user.strip() if export_user else "",
                limit=int(export_limit)
            )
        except Exception as e:
            st.error("Unable to load component.")
            st.exception(e)
            df_export = pd.DataFrame()
            
        if not df_export.empty:
            try:
                st.success(f"Successfully staged {len(df_export)} alerts for export!")
                
                # Prepare CSV
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Filtered Alerts (CSV)",
                    data=csv_data,
                    file_name="shatrubodh_alerts_export.csv",
                    mime="text/csv",
                    key="rep_download_csv_btn"
                )
            except Exception as e:
                st.error("Unable to load component.")
                st.exception(e)
        else:
            st.warning("No records matched the selected query parameters.")
