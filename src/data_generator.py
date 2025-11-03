
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_mock_data(num_rows=2000):
    users = [fake.user_name() for _ in range(50)]
    ips = [fake.ipv4() for _ in range(100)]
    devices = [f"DESKTOP-{fake.hexify(text='^^^^^^^^')}" for _ in range(50)]
    processes = ["powershell.exe", "cmd.exe", "svchost.exe", "python.exe", "ResearchClient.exe", "Game.exe"]
    
    actions = ["login", "logout", "file_access", "file_upload", "file_download", "privilege_change", "process_execution", "usb_plugin"]
    privileges = ["user", "admin"]

    data = []
    for _ in range(num_rows):
        user = np.random.choice(users)
        timestamp = datetime.now() - timedelta(days=np.random.randint(0, 30), hours=np.random.randint(0, 24), minutes=np.random.randint(0, 60))
        action = np.random.choice(actions, p=[0.2, 0.2, 0.2, 0.1, 0.1, 0.05, 0.1, 0.05])
        
        record = {
            'timestamp': timestamp, 'user_id': user, 'action_type': action,
            'resource': "N/A", 'device': np.random.choice(devices),
            'remote_ip': np.random.choice(ips), 'privilege_level': "user",
            'bytes_transferred': 0, 'process_name': "N/A", 'usb_device': "N/A"
        }

        if action in ["file_access", "file_upload", "file_download"]:
            record['resource'] = fake.file_path(depth=4, category='text')
            record['bytes_transferred'] = np.random.randint(1024, 1024 * 1024)
        elif action == "privilege_change":
            record['privilege_level'] = "admin"
        elif action == "process_execution":
            record['process_name'] = np.random.choice(processes)
        elif action == "usb_plugin":
            record['usb_device'] = f"Kingston_DataTraveler_{fake.hexify(text='^^^^')}"

        # Inject anomalies
        if np.random.rand() < 0.05:
            anomaly_type = np.random.choice(['off_hours', 'large_download', 'suspicious_process', 'privilege_abuse'])
            if anomaly_type == 'off_hours':
                record['timestamp'] = record['timestamp'].replace(hour=np.random.randint(0, 5))
            elif anomaly_type == 'large_download':
                record['action_type'] = 'file_download'
                record['bytes_transferred'] = np.random.randint(1024 * 1024 * 50, 1024 * 1024 * 200)
            elif anomaly_type == 'suspicious_process':
                record['process_name'] = "mimikatz.exe"
            elif anomaly_type == 'privilege_abuse':
                record['privilege_level'] = 'admin'
                record['action_type'] = 'file_access'
                record['resource'] = "/etc/shadow"

        data.append(record)

    df = pd.DataFrame(data)
    df.to_csv("src/sample_data.csv", index=False)
    return "src/sample_data.csv"

if __name__ == "__main__":
    generate_mock_data()
