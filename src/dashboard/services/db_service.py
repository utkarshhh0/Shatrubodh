# src/dashboard/services/db_service.py

import sqlite3
import pandas as pd
import streamlit as st
import os

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "shatrubodh.db")

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection with Foreign Keys, WAL, and safe sync settings."""
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    return conn

def get_alert_counts(db_path: str = DEFAULT_DB_PATH) -> dict:
    """
    Returns aggregate alert status count dictionary for KPI metrics.
    No caching applied to ensure real-time SLA metrics are correct.
    """
    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        
        # 1. Total counts by severity
        cursor.execute("SELECT severity, COUNT(*) FROM alerts GROUP BY severity")
        securities = dict(cursor.fetchall())
        
        # 2. Count by status
        cursor.execute("SELECT status, COUNT(*) FROM alerts GROUP BY status")
        statuses = dict(cursor.fetchall())
        
        return {
            'total': sum(securities.values()),
            'critical': securities.get('Critical', 0),
            'high': securities.get('High', 0),
            'medium': securities.get('Medium', 0),
            'new': statuses.get('New', 0),
            'in_progress': statuses.get('In_Progress', 0),
            'resolved': statuses.get('Resolved', 0),
            'false_positive': statuses.get('False_Positive', 0)
        }
    finally:
        if cursor:
            cursor.close()
        conn.close()

def get_alert_queue(
    status_filters: list = None,
    severity_filters: list = None,
    user_id_search: str = "",
    start_date: str = None,
    end_date: str = None,
    limit: int = 50,
    offset: int = 0,
    db_path: str = DEFAULT_DB_PATH
) -> pd.DataFrame:
    """
    Retrieves a paginated list of alerts filtered by user settings.
    No caching applied to allow dynamic lifecycle triaging.
    """
    import re
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    if status_filters is not None:
        if not isinstance(status_filters, (list, tuple)):
            raise TypeError("status_filters must be a list or tuple")
        valid_statuses = {'New', 'In_Progress', 'Resolved', 'False_Positive'}
        for s in status_filters:
            if s not in valid_statuses:
                raise ValueError(f"Invalid status filter value: {s}")

    if severity_filters is not None:
        if not isinstance(severity_filters, (list, tuple)):
            raise TypeError("severity_filters must be a list or tuple")
        valid_severities = {'Medium', 'High', 'Critical'}
        for s in severity_filters:
            if s not in valid_severities:
                raise ValueError(f"Invalid severity filter value: {s}")

    if not isinstance(user_id_search, str):
        raise TypeError("user_id_search must be a string")

    if start_date is not None:
        if not isinstance(start_date, str):
            raise TypeError("start_date must be a string")
        if not date_pattern.match(start_date):
            raise ValueError("start_date must be in YYYY-MM-DD format")

    if end_date is not None:
        if not isinstance(end_date, str):
            raise TypeError("end_date must be a string")
        if not date_pattern.match(end_date):
            raise ValueError("end_date must be in YYYY-MM-DD format")

    if not isinstance(limit, int) or limit < 0:
        raise TypeError("limit must be a non-negative integer")
    if not isinstance(offset, int) or offset < 0:
        raise TypeError("offset must be a non-negative integer")

    conn = get_connection(db_path)
    try:
        conditions = ["1=1"]
        params = {}
        
        if status_filters:
            placeholders = ", ".join(f":status_{i}" for i in range(len(status_filters)))
            conditions.append(f"a.status IN ({placeholders})")
            for i, val in enumerate(status_filters):
                params[f"status_{i}"] = val
                
        if severity_filters:
            placeholders = ", ".join(f":sev_{i}" for i in range(len(severity_filters)))
            conditions.append(f"a.severity IN ({placeholders})")
            for i, val in enumerate(severity_filters):
                params[f"sev_{i}"] = val
                
        if user_id_search:
            clean_search = user_id_search.strip()
            # Compile exact CMU CERT user ID pattern (e.g. 3-4 letters followed by 4 digits)
            import re
            cert_pattern = re.compile(r'^[A-Za-z]{3,4}\d{4}$')
            if cert_pattern.match(clean_search):
                conditions.append("a.user_id = :user_id")
                params["user_id"] = clean_search
            else:
                conditions.append("a.user_id LIKE :user_id")
                params["user_id"] = f"%{clean_search}%"
            
        if start_date:
            conditions.append("a.alert_date >= :start_date")
            params["start_date"] = start_date
            
        if end_date:
            conditions.append("a.alert_date <= :end_date")
            params["end_date"] = end_date
            
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT 
                a.alert_id,
                a.profile_id,
                a.user_id,
                a.alert_date,
                a.created_at,
                a.severity,
                a.status,
                a.assigned_to,
                a.reasons,
                a.evidence_json,
                a.analyst_notes,
                r.risk_score
            FROM alerts a
            JOIN risk_scores r ON a.profile_id = r.profile_id
            WHERE {where_clause}
            ORDER BY r.risk_score DESC
            LIMIT :limit OFFSET :offset
        """
        params["limit"] = limit
        params["offset"] = offset
        
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()

def update_alert_status(
    alert_id: str,
    status: str,
    assigned_to: str,
    analyst_notes: str,
    db_path: str = DEFAULT_DB_PATH
):
    """
    Executes raw SQL update transaction to persist operational status changes.
    """
    if not isinstance(alert_id, str) or not alert_id:
        raise ValueError("alert_id must be a non-empty string")
    if status not in {'New', 'In_Progress', 'Resolved', 'False_Positive'}:
        raise ValueError(f"Invalid status value: {status}")
    if assigned_to is not None and not isinstance(assigned_to, str):
        raise TypeError("assigned_to must be None or a string")
    if analyst_notes is not None and not isinstance(analyst_notes, str):
        raise TypeError("analyst_notes must be None or a string")

    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alerts 
            SET status = ?, assigned_to = ?, analyst_notes = ? 
            WHERE alert_id = ?
        """, (status, assigned_to, analyst_notes, alert_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        conn.close()

@st.cache_data(ttl=3600)
def get_user_demographics(user_id: str, db_path: str = DEFAULT_DB_PATH) -> dict:
    """
    Retrieves user profile demographics context from users table.
    Cached for 1 hour.
    """
    if not isinstance(user_id, str) or not user_id:
        raise ValueError("user_id must be a non-empty string")

    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, department, role, manager, team FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return {}
        return {
            'name': row[0],
            'department': row[1],
            'role': row[2],
            'manager': row[3],
            'team': row[4]
        }
    finally:
        if cursor:
            cursor.close()
        conn.close()

@st.cache_data(ttl=600)
def get_user_rolling_history(user_id: str, alert_date: str, db_path: str = DEFAULT_DB_PATH) -> list:
    """
    Fetches the 30 most recent behavioral records for a user prior to the alert date.
    Cached for 10 minutes (keyed by user_id and alert_date).
    """
    import re
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not isinstance(user_id, str) or not user_id:
        raise ValueError("user_id must be a non-empty string")
    if not isinstance(alert_date, str) or not date_pattern.match(alert_date):
        raise ValueError("alert_date must be in YYYY-MM-DD format")

    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                logon_count, logoff_count, after_hours_logins, usb_insertions,
                file_write_count, file_copy_to_usb, file_delete_count,
                emails_sent, attachments_sent, email_exfil_bytes, unique_pcs, total_events
            FROM behavior_profiles
            WHERE user_id = ?
              AND profile_date < ?
            ORDER BY profile_date DESC
            LIMIT 30
        """, (user_id, alert_date))
        rows = cursor.fetchall()
        return rows
    finally:
        if cursor:
            cursor.close()
        conn.close()

@st.cache_data(ttl=600)
def get_cohort_population_history(department: str, role: str, alert_date: str, db_path: str = DEFAULT_DB_PATH) -> list:
    """
    Fetches peer group cohort profiles (same role/dept) in a 90-day window.
    Cached for 10 minutes (keyed by department, role, and alert_date).
    """
    import re
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not isinstance(department, str) or not department:
        raise ValueError("department must be a non-empty string")
    if not isinstance(role, str) or not role:
        raise ValueError("role must be a non-empty string")
    if not isinstance(alert_date, str) or not date_pattern.match(alert_date):
        raise ValueError("alert_date must be in YYYY-MM-DD format")

    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                logon_count, logoff_count, after_hours_logins, usb_insertions,
                file_write_count, file_copy_to_usb, file_delete_count,
                emails_sent, attachments_sent, email_exfil_bytes, unique_pcs, total_events
            FROM behavior_profiles
            WHERE department = ?
              AND role = ?
              AND profile_date < ?
              AND profile_date >= DATE(?, '-90 days')
        """, (department, role, alert_date, alert_date))
        rows = cursor.fetchall()
        return rows
    finally:
        if cursor:
            cursor.close()
        conn.close()

def get_department_threat_density(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Queries alert counts grouped by department for operational reporting charts.
    """
    conn = get_connection(db_path)
    try:
        query = """
            SELECT 
                u.department, 
                COUNT(a.alert_id) AS alert_count,
                SUM(CASE WHEN a.severity = 'Critical' THEN 1 ELSE 0 END) AS critical_count,
                SUM(CASE WHEN a.severity = 'High' THEN 1 ELSE 0 END) AS high_count,
                SUM(CASE WHEN a.severity = 'Medium' THEN 1 ELSE 0 END) AS medium_count
            FROM alerts a
            JOIN users u ON a.user_id = u.user_id
            GROUP BY u.department
            ORDER BY alert_count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

def get_role_threat_density(db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Queries alert counts grouped by role for operational reporting charts.
    """
    conn = get_connection(db_path)
    try:
        query = """
            SELECT 
                u.role, 
                COUNT(a.alert_id) AS alert_count
            FROM alerts a
            JOIN users u ON a.user_id = u.user_id
            GROUP BY u.role
            ORDER BY alert_count DESC
            LIMIT 10
        """
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

def get_user_risk_timeline(user_id: str, db_path: str = DEFAULT_DB_PATH) -> pd.DataFrame:
    """
    Queries risk scores over time for a specific user to render trend lines.
    """
    if not isinstance(user_id, str) or not user_id:
        raise ValueError("user_id must be a non-empty string")

    conn = get_connection(db_path)
    try:
        query = """
            SELECT 
                b.profile_date, 
                COALESCE(r.risk_score, 0.0) AS risk_score
            FROM behavior_profiles b
            LEFT JOIN risk_scores r ON b.profile_id = r.profile_id
            WHERE b.user_id = :user_id
            ORDER BY b.profile_date ASC
        """
        df = pd.read_sql_query(query, conn, params={"user_id": user_id})
        return df
    finally:
        conn.close()

def get_user_alerts_dates(user_id: str, db_path: str = DEFAULT_DB_PATH) -> list:
    """
    Retrieves all dates where the user triggered an alert.
    """
    if not isinstance(user_id, str) or not user_id:
        raise ValueError("user_id must be a non-empty string")

    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT alert_date FROM alerts WHERE user_id = ? ORDER BY alert_date DESC", (user_id,))
        rows = [r[0] for r in cursor.fetchall()]
        return rows
    finally:
        if cursor:
            cursor.close()
        conn.close()

def get_alert_by_user_date(user_id: str, alert_date: str, db_path: str = DEFAULT_DB_PATH) -> dict:
    """
    Retrieves a single alert record for a user on a specific date.
    """
    import re
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not isinstance(user_id, str) or not user_id:
        raise ValueError("user_id must be a non-empty string")
    if not isinstance(alert_date, str) or not date_pattern.match(alert_date):
        raise ValueError("alert_date must be in YYYY-MM-DD format")

    conn = get_connection(db_path)
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT alert_id, reasons, evidence_json, severity, status, assigned_to, analyst_notes 
            FROM alerts 
            WHERE user_id = ? AND alert_date = ?
        """, (user_id, alert_date))
        row = cursor.fetchone()
        if not row:
            return {}
        return {
            'alert_id': row[0],
            'reasons': row[1],
            'evidence_json': row[2],
            'severity': row[3],
            'status': row[4],
            'assigned_to': row[5],
            'analyst_notes': row[6]
        }
    finally:
        if cursor:
            cursor.close()
        conn.close()
