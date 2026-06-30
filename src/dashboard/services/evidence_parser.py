# src/dashboard/services/evidence_parser.py

import json
import pandas as pd
import numpy as np

METRICS_COLUMNS = [
    'logon_count', 'logoff_count', 'after_hours_logins', 'usb_insertions',
    'file_write_count', 'file_copy_to_usb', 'file_delete_count',
    'emails_sent', 'attachments_sent', 'email_exfil_bytes', 'unique_pcs', 'total_events'
]

def parse_evidence(evidence_json_str: str) -> dict:
    """
    Parses the evidence JSON string into a structured dictionary.
    """
    try:
        return json.loads(evidence_json_str)
    except Exception:
        return {}

def format_metric_value(metric_name: str, value) -> str:
    """
    Formats the raw value of a metric into a readable string (e.g. bytes to MB).
    """
    if value is None:
        return "0"
        
    if metric_name == 'email_exfil_bytes':
        mb = float(value) / (1024 * 1024)
        return f"{mb:.2f} MB"
        
    if isinstance(value, float):
        return f"{value:.2f}"
        
    return str(int(value)) if isinstance(value, (int, float)) and value.is_integer() else str(value)

def compute_comparisons(
    alert_evidence: dict,
    user_history_rows: list,
    cohort_history_rows: list
) -> pd.DataFrame:
    """
    Computes absolute, percentage difference, and Z-score for the 12 core metrics.
    Handles zero std-dev bounds and flags insufficient data.
    """
    comparison_data = []
    
    # 1. Load baseline dataframes
    df_user = pd.DataFrame(user_history_rows, columns=METRICS_COLUMNS) if user_history_rows else pd.DataFrame()
    df_cohort = pd.DataFrame(cohort_history_rows, columns=METRICS_COLUMNS) if cohort_history_rows else pd.DataFrame()
    
    user_means = df_user.mean() if not df_user.empty else None
    user_stds = df_user.std(ddof=0) if not df_user.empty else None
    
    cohort_means = df_cohort.mean() if not df_cohort.empty else None
    cohort_stds = df_cohort.std(ddof=0) if not df_cohort.empty else None
    
    epsilon = 1e-5
    
    for metric in METRICS_COLUMNS:
        x_alert = float(alert_evidence.get(metric, 0))
        
        # --- A. User Baseline ---
        if user_history_rows and len(user_history_rows) >= 10:
            u_mean = float(user_means[metric])
            u_std = float(user_stds[metric])
            
            u_diff = x_alert - u_mean
            
            # Percentage Diff
            u_pct = (u_diff / (u_mean + epsilon)) * 100.0
            u_pct_str = f"{u_pct:+.1f}%" if u_mean > 0 or abs(u_diff) > 0 else "0.0%"
            if u_mean == 0 and x_alert > 0:
                u_pct_str = "First Occurrence"
                
            # Z-Score
            if u_std > 0:
                z_val = u_diff / u_std
                u_z_str = f"{z_val:+.2f}"
            else:
                u_z_str = "0.00" if x_alert == u_mean else ("First Occurrence" if u_mean == 0 else "Critical Deviation")
                
            u_mean_str = format_metric_value(metric, u_mean)
        else:
            u_mean_str = "Insufficient Data"
            u_pct_str = "N/A"
            u_z_str = "N/A"
            
        # --- B. Cohort Baseline ---
        if cohort_history_rows:
            c_mean = float(cohort_means[metric])
            c_std = float(cohort_stds[metric])
            
            c_diff = x_alert - c_mean
            
            # Percentage Diff
            c_pct = (c_diff / (c_mean + epsilon)) * 100.0
            c_pct_str = f"{c_pct:+.1f}%" if c_mean > 0 or abs(c_diff) > 0 else "0.0%"
            if c_mean == 0 and x_alert > 0:
                c_pct_str = "First Occurrence"
                
            # Z-Score
            if c_std > 0:
                z_val = c_diff / c_std
                c_z_str = f"{z_val:+.2f}"
            else:
                c_z_str = "0.00" if x_alert == c_mean else ("First Occurrence" if c_mean == 0 else "Critical Deviation")
                
            c_mean_str = format_metric_value(metric, c_mean)
        else:
            c_mean_str = "Insufficient Data"
            c_pct_str = "N/A"
            c_z_str = "N/A"
            
        comparison_data.append({
            'Metric': metric.replace('_', ' ').title(),
            'Alert Value': format_metric_value(metric, x_alert),
            'User Mean': u_mean_str,
            'User Dev (Z)': u_z_str,
            'User Dev (%)': u_pct_str,
            'Cohort Mean': c_mean_str,
            'Cohort Dev (Z)': c_z_str,
            'Cohort Dev (%)': c_z_str if c_z_str in ["First Occurrence", "Critical Deviation"] else c_pct_str
        })
        
    return pd.DataFrame(comparison_data)
