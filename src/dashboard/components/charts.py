# src/dashboard/components/charts.py

import pandas as pd
import streamlit as st

def plot_risk_timeline(df: pd.DataFrame):
    """
    Plots a chronological risk score trend line for a specific user.
    """
    try:
        if df.empty:
            st.info("No risk timeline data available.")
            return
        
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
        if df.empty:
            st.info("No department threat density data available.")
            return
        
        # We want to display total alerts per department
        chart_df = df[['department', 'alert_count']].copy()
        chart_df = chart_df.rename(columns={'alert_count': 'Alert Count'})
        
        st.bar_chart(chart_df, x="department", y="Alert Count")
    except Exception as e:
        st.error("Unable to load component.")
        st.exception(e)
