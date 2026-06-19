# src/collectors/ldap_collector.py

import os
import glob
import sys
import pandas as pd

# Safeguard imports when running directly or as a package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas.event_schema import validate_user_profile

def collect_users_chronologically(dataset_dir: str) -> dict:
    """
    Reads users.csv and monthly LDAP snapshots in chronological order.
    Consolidates them into a dictionary keyed by user_id containing their latest profile state.
    
    Returns:
        dict: { user_id: { 'user_id': ..., 'name': ..., 'department': ..., 'role': ..., 'manager': ..., 'team': ... } }
    """
    users_dict = {}
    
    # 1. Process users.csv (baseline)
    users_csv_path = os.path.join(dataset_dir, "users.csv")
    if not os.path.exists(users_csv_path):
        raise FileNotFoundError(f"Base users CSV file not found: {users_csv_path}")
        
    df_users = pd.read_csv(users_csv_path)
    for _, row in df_users.iterrows():
        raw_user = {
            "user_id": str(row.get("user_id", "")).strip(),
            "name": str(row.get("employee_name", "")).strip(),
            "department": str(row.get("department", "")).strip(),
            "role": str(row.get("role", "")).strip(),
            "manager": str(row.get("supervisor", "")).strip(),
            "team": str(row.get("team", "")).strip()
        }
        try:
            validated = validate_user_profile(raw_user)
            users_dict[validated["user_id"]] = validated
        except ValueError as e:
            # Skip invalid users and continue
            print(f"Skipping invalid base user row {raw_user.get('user_id')}: {e}", file=sys.stderr)
            
    # 2. Process LDAP snapshots chronologically (*.csv in LDAP folder sorted alphabetically)
    ldap_dir = os.path.join(dataset_dir, "LDAP")
    if os.path.exists(ldap_dir):
        # Sort files (e.g. 2010-12.csv, 2011-01.csv, etc.) to enforce chronological ordering
        snapshot_files = sorted(glob.glob(os.path.join(ldap_dir, "*.csv")))
        for snap_file in snapshot_files:
            df_snap = pd.read_csv(snap_file)
            for _, row in df_snap.iterrows():
                raw_user = {
                    "user_id": str(row.get("user_id", "")).strip(),
                    "name": str(row.get("employee_name", "")).strip(),
                    "department": str(row.get("department", "")).strip(),
                    "role": str(row.get("role", "")).strip(),
                    "manager": str(row.get("supervisor", "")).strip(),
                    "team": str(row.get("team", "")).strip()
                }
                try:
                    validated = validate_user_profile(raw_user)
                    # Override previous records with latest snapshot values (upsert)
                    users_dict[validated["user_id"]] = validated
                except ValueError as e:
                    print(f"Skipping invalid snapshot user row in {os.path.basename(snap_file)}: {e}", file=sys.stderr)
                    
    return users_dict


def build_user_lookup(users_dict: dict) -> dict:
    """
    Transforms the consolidated user profiles into a fast, lightweight lookup mapping:
    user_id -> { "department": ..., "role": ... }
    """
    return {
        uid: {
            "department": profile["department"],
            "role": profile["role"]
        }
        for uid, profile in users_dict.items()
    }


if __name__ == "__main__":
    # Test script locally
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_dataset = os.path.join(workspace_dir, "src", "dataset")
    
    if os.path.exists(test_dataset):
        print(f"Testing LDAP Ingestion from: {test_dataset}")
        users = collect_users_chronologically(test_dataset)
        print(f"Ingested {len(users)} unique user profiles.")
        lookup = build_user_lookup(users)
        print(f"User Lookup map populated. Sample check for NFP2441: {lookup.get('NFP2441')}")
    else:
        print(f"Dataset path not found for local verification: {test_dataset}")
