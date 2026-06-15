import requests
from datetime import datetime
import numpy as np

response = requests.get("https://httpbin.org/json")
print(f"Status: {response.status_code}")
print(f"Run time: {datetime.now()}")
print(f"Check")
print(f"{np.__version__}")