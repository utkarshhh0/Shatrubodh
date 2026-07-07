import streamlit as st
import pandas as pd
import os
import sys

# Ensure relative imports from src/ are correctly resolved
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard.pages.alert_queue import render_alert_queue
from dashboard.pages.threat_hunter import render_threat_hunter
from dashboard.pages.reports import render_reports

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
            v0.10.5 |
            &copy; 2026 Utkarsh Gupta |
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
    st.caption(f"Insider Threat database loaded. Last updated: {pd.to_datetime('now')}")

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Threat Hunter", "System & Reports"])

    with tab1:
        render_alert_queue()
    with tab2:
        render_threat_hunter()
    with tab3:
        render_reports()

    render_footer()


if __name__ == "__main__":
    main()