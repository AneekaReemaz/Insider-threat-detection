import random
import pandas as pd
from faker import Faker
from datetime import timedelta

fake = Faker()

# Step 1: Generate 100 users
users = [f"EMP{str(i).zfill(3)}" for i in range(1, 101)]

# Step 2: Define normal actions
actions = ["login", "file_access", "command_execution", "email_sent"]
resources = ["server1", "server2", "file1.txt", "file2.pdf", "report.docx", "db_backup.sql"]

records = []

# Step 3: Generate normal user behavior
for _ in range(5700):  # ~95% normal
    user = random.choice(users)
    timestamp = fake.date_time_this_year()
    action = random.choice(actions)
    success = 1 if action != "login" else random.choice([0, 1])  # occasional failed login
    resource = random.choice(resources)
    ip = fake.ipv4_private()  # local/private IPs mostly

    records.append([user, timestamp, action, success, resource, ip, 0])  # label 0 = normal

# Step 4: Inject anomalies (~5%)
for _ in range(300):  
    user = random.choice(users)
    anomaly_type = random.choice(["off_hours", "failed_login", "mass_file_access", "unusual_ip"])

    if anomaly_type == "off_hours":
        # login at 3 AM
        timestamp = fake.date_time_this_year().replace(hour=random.choice([2, 3, 4]))
        records.append([user, timestamp, "login", 1, "server1", fake.ipv4_private(), 1])

    elif anomaly_type == "failed_login":
        # 2 quick failed logins
        base_time = fake.date_time_this_year()
        for i in range(2):
            timestamp = base_time + timedelta(seconds=i * 10)
            records.append([user, timestamp, "login", 0, "server1", fake.ipv4_private(), 1])

    elif anomaly_type == "mass_file_access":
        # accessing 5 files in 1 minute
        base_time = fake.date_time_this_year()
        for i in range(5):
            timestamp = base_time + timedelta(seconds=i * 10)
            records.append([user, timestamp, "file_access", 1, random.choice(resources), fake.ipv4_private(), 1])

    elif anomaly_type == "unusual_ip":
        # login from unusual public IP
        timestamp = fake.date_time_this_year()
        records.append([user, timestamp, "login", 1, "server1", fake.ipv4_public(), 1])

# Step 5: Create dataframe
df = pd.DataFrame(records, columns=[
    "user_id", "timestamp", "action_type", "success", "resource_accessed", "ip", "label"
])

# Step 6: Save dataset
df.to_csv("synthetic_uba_logs.csv", index=False)
print("✅ Dataset generated: synthetic_uba_logs.csv")
print("Total logs:", len(df))
print("Anomalies:", df['label'].sum(), "≈", round((df['label'].sum()/len(df))*100, 2), "%")
print(df.head(10))
