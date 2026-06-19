# src/collectors/cert_collector.py

import os
import sys
import pandas as pd

def _verify_file_exists(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Authoritative CERT CSV file not found: {path}")


def stream_logon_events(dataset_dir: str, chunk_size: int = 50000):
    """
    Yields list of raw logon records in memory-safe chunks.
    Fields: id, date, user, pc, activity
    """
    path = os.path.join(dataset_dir, "logon_filtered.csv")
    _verify_file_exists(path)
    
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        # Fill NaNs with empty strings or default placeholders to avoid validation issues
        chunk = chunk.fillna("none")
        yield chunk.to_dict(orient="records")


def stream_device_events(dataset_dir: str, chunk_size: int = 50000):
    """
    Yields list of raw device records in memory-safe chunks.
    Fields: id, date, user, pc, file_tree, activity
    """
    path = os.path.join(dataset_dir, "device_filtered.csv")
    _verify_file_exists(path)
    
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        chunk = chunk.fillna("none")
        yield chunk.to_dict(orient="records")


def stream_file_events(dataset_dir: str, chunk_size: int = 50000):
    """
    Yields list of raw file records in memory-safe chunks.
    Fields: id, date, user, pc, filename, activity, to_removable_media, from_removable_media, content
    """
    path = os.path.join(dataset_dir, "file_filtered.csv")
    _verify_file_exists(path)
    
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        chunk = chunk.fillna("none")
        yield chunk.to_dict(orient="records")


def stream_email_events(dataset_dir: str, chunk_size: int = 50000):
    """
    Yields list of raw email records in memory-safe chunks.
    Fields: id, date, user, pc, to, cc, bcc, from, activity, size, attachments, content
    """
    path = os.path.join(dataset_dir, "email_filtered.csv")
    _verify_file_exists(path)
    
    for chunk in pd.read_csv(path, chunksize=chunk_size):
        chunk = chunk.fillna("none")
        yield chunk.to_dict(orient="records")


if __name__ == "__main__":
    # Test script locally with tiny chunk sizes
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_dataset = os.path.join(workspace_dir, "src", "dataset")
    
    if os.path.exists(test_dataset):
        print(f"Testing CERT Ingestion from: {test_dataset}")
        
        try:
            print("1. Testing Logon Reader...")
            logon_gen = stream_logon_events(test_dataset, chunk_size=5)
            first_logon_chunk = next(logon_gen)
            print(f"Read {len(first_logon_chunk)} rows. Sample: {first_logon_chunk[0]}")
            
            print("2. Testing Device Reader...")
            device_gen = stream_device_events(test_dataset, chunk_size=5)
            first_device_chunk = next(device_gen)
            print(f"Read {len(first_device_chunk)} rows. Sample: {first_device_chunk[0]}")
            
            print("3. Testing File Reader...")
            file_gen = stream_file_events(test_dataset, chunk_size=5)
            first_file_chunk = next(file_gen)
            print(f"Read {len(first_file_chunk)} rows. Sample: {first_file_chunk[0]}")
            
            print("4. Testing Email Reader...")
            email_gen = stream_email_events(test_dataset, chunk_size=5)
            first_email_chunk = next(email_gen)
            print(f"Read {len(first_email_chunk)} rows. Sample: {first_email_chunk[0]}")
            
            print("All collectors operational.")
        except Exception as e:
            print(f"Collector verification failed: {e}", file=sys.stderr)
    else:
        print(f"Dataset path not found for local verification: {test_dataset}")
