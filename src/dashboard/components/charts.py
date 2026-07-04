# src/dashboard/components/charts.py

import pandas as pd
import streamlit as st

def plot_risk_timeline(df: pd.DataFrame):
    """
    Plots a chronological risk score trend line for a specific user.
    """
    try:
        if df is None:
            raise TypeError("Timeline DataFrame cannot be None")
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Timeline input must be a pandas DataFrame")
            
        if df.empty:
            st.info("No risk timeline data available.")
            return
            
        if 'profile_date' not in df.columns:
            raise ValueError("Timeline DataFrame missing 'profile_date' column")
        if 'risk_score' not in df.columns:
            raise ValueError("Timeline DataFrame missing 'risk_score' column")
        if not df['risk_score'].between(0.0, 100.0).all():
            raise ValueError("risk_score values must be in range [0, 100]")
        
        chart_df = df.copy()
        chart_df['profile_date'] = pd.to_datetime(chart_df['profile_date'])
        chart_df = chart_df.sort_values('profile_date').set_index('profile_date')
        
        st.line_chart(chart_df['risk_score'])
    except Exception as e:
        st.error("Unable to load component.")
        st.exception(e)

def plot_metric_comparison(metric_label: str, alert_val: float, user_mean: float, cohort_mean: float):
    """
    Plots a bar chart comparing the alert day's metric value against user and cohort baselines.
    """
    try:
        if not isinstance(metric_label, str):
            raise TypeError("metric_label must be a string")
        if not isinstance(alert_val, (int, float)) or not isinstance(user_mean, (int, float)) or not isinstance(cohort_mean, (int, float)):
            raise TypeError("Alert value, user mean, and cohort mean must be numeric values")
            
        comparison_df = pd.DataFrame({
            "Category": ["Current Alert", "User Baseline (Mean)", "Cohort Baseline (Mean)"],
            "Value": [alert_val, user_mean, cohort_mean]
        })
        
        st.bar_chart(comparison_df, x="Category", y="Value")
    except Exception as e:
        st.error("Unable to load component.")
        st.exception(e)

def plot_department_distribution(df: pd.DataFrame):
    """
    Plots the threat distribution across departments using a bar chart.
    """
    try:
        if df is None:
            raise TypeError("Department density DataFrame cannot be None")
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Department density input must be a pandas DataFrame")
            
        if df.empty:
            st.info("No department threat density data available.")
            return
            
        if 'department' not in df.columns:
            raise ValueError("Department density DataFrame missing 'department' column")
        if 'alert_count' not in df.columns:
            raise ValueError("Department density DataFrame missing 'alert_count' column")
        
        # We want to display total alerts per department
        chart_df = df[['department', 'alert_count']].copy()
        chart_df = chart_df.rename(columns={'alert_count': 'Alert Count'})
        
        st.bar_chart(chart_df, x="department", y="Alert Count")
    except Exception as e:
        st.error("Unable to load component.")
        st.exception(e)
