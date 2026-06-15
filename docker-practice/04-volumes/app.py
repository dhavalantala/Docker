import os
from datetime import datetime

LOG_FILE = "/app/logs/requests.log"

os.makedirs("/app/logs", exist_ok=True)

def log_request(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} — {message}\n")

log_request("Container started")
print("Logged a request. Check logs/requests.log")