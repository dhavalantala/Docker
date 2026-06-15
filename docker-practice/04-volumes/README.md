# Concept 4 — Volumes & Bind Mounts 💾

> How containers persist data, share files with your host machine,
> and enable hot-reload development workflows.

---

## 📁 Folder Structure

```
04-volumes/
├── app.py                  # Logging demo (named volume)
├── Dockerfile              # Basic python image
├── logs/                   # Created by bind mount (gitignore this)
└── hot-reload/
    ├── app.py              # Flask app for hot reload demo
    ├── requirements.txt
    └── Dockerfile
```

---

## 🧠 The Core Problem — Containers Are Stateless

Every `docker run` creates a **brand new container** with a **clean filesystem**.

```bash
docker run volume-demo:v1   # Writes logs/requests.log inside container
# Container exits → filesystem is GONE

docker run volume-demo:v1   # Brand new container, no log file exists
docker run volume-demo:v1 cat /app/logs/requests.log
# cat: No such file or directory ❌
```

This is not a bug — it is by design. Containers are meant to be **ephemeral** (disposable).

**But what if you need data to survive?** → That's what volumes solve.

---

## 🗂️ Three Types of Storage in Docker

```
┌─────────────────────────────────────────────────────────┐
│                     Your Mac (Host)                     │
│                                                         │
│   /Users/dhaval/docker-practice/04-volumes/logs/  ←──Bind Mount
│                                                         │
│   Docker Managed Storage (/var/lib/docker/volumes/) ←──Named Volume
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Container Filesystem                │   │
│  │                                                  │   │
│  │   /app/         ← Image layers (read/write)      │   │
│  │   /app/logs/    ← tmpfs or mounted volume        │   │
│  │                                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

| Type | Flag | Who Controls Path | Visible on Mac | Best For |
|------|------|-------------------|----------------|----------|
| Named Volume | `-v ml-logs:/app/logs` | Docker | ❌ Not directly | Persisting DB data, logs |
| Bind Mount | `-v $(pwd)/logs:/app/logs` | You | ✅ Yes | Local dev, hot reload |
| tmpfs | `--tmpfs /app/temp` | RAM only | ❌ No | Sensitive temp data |

---

## 📦 Solution 1 — Named Volumes

Docker creates and manages the storage location for you.

```bash
# Syntax: -v VOLUME_NAME:CONTAINER_PATH
docker run -v ml-logs:/app/logs volume-demo:v1
```

### How it works

```
First run:
  Docker sees "ml-logs" → doesn't exist → creates it
  Container writes to /app/logs → data goes into ml-logs volume

Container exits → ml-logs volume SURVIVES ✅

Second run:
  Docker sees "ml-logs" → exists → mounts it
  Container reads /app/logs → sees previous data ✅
```

### Volume lifecycle commands

```bash
# List all volumes
docker volume ls

# Inspect a volume (find where Docker stores it on your Mac)
docker volume inspect ml-logs

# Create a volume manually
docker volume create my-data

# Remove a volume
docker volume rm ml-logs

# Remove ALL unused volumes (careful!)
docker volume prune
```

### What docker volume inspect shows

```json
[
    {
        "Name": "ml-logs",
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/ml-logs/_data",
        "Scope": "local"
    }
]
```

> On Mac, Docker Desktop runs inside a Linux VM.
> `/var/lib/docker/volumes/` is inside that VM, not directly on your Mac.
> That's why bind mounts are better for local dev — you can actually see the files.

---

## 📂 Solution 2 — Bind Mounts

You specify the exact path on your Mac. Container reads/writes there directly.

```bash
# Syntax: -v /absolute/mac/path:CONTAINER_PATH
docker run -v $(pwd)/logs:/app/logs volume-demo:v1

# $(pwd) expands to your current directory
# e.g. /Users/dhaval/docker-practice/04-volumes
```

### How it works

```
Your Mac                          Container
─────────────────                 ─────────────────
/Users/dhaval/                    /app/logs/
docker-practice/      ←────────►  requests.log
04-volumes/logs/
requests.log

Both sides see the SAME file in real time
```

### Read the file directly from your Mac

```bash
# No Docker needed — it's just a regular file on your Mac
cat logs/requests.log
open logs/             # Opens in Finder!
code logs/requests.log # Opens in VS Code
```

---

## 🔥 Solution 3 — Bind Mount for Hot Reload (Most Useful!)

Mount your entire source code folder into the container.
Edit on Mac → container sees it immediately → no rebuild needed.

```bash
# Mount current directory OVER /app in the container
docker run -p 8080:5000 \
  -v $(pwd):/app \
  --name hot-app \
  hot-reload:v1
```

### What happens

```
Your Mac                    Container
─────────────────           ─────────────────
$(pwd)/app.py   ──────────► /app/app.py  (same file!)
$(pwd)/         ──────────► /app/

You edit app.py on Mac
Flask debug mode detects change
Container auto-reloads
Browser refresh → new code ✅
```

> ⚠️ The bind mount OVERRIDES what was COPYed in the Dockerfile.
> That's intentional — your local code takes priority during development.
> In production, you use the COPYed version (no bind mount).

---

## 🔄 Volume vs Bind Mount — When to Use Which

### Use Named Volume when:
- Running a **database** (PostgreSQL, MySQL, MongoDB)
- Persisting **model weights** downloaded at runtime
- Storing **logs in production**
- You don't need to access files directly from Mac

```bash
# Example: Postgres with named volume
docker run -v postgres-data:/var/lib/postgresql/data postgres:15
```

### Use Bind Mount when:
- **Local development** — edit code, see changes instantly
- Reading a **dataset from your Mac** into the container
- Writing **output files** you want to access on your Mac
- **Debugging** — inspect files the container writes

```bash
# Example: ML training reading dataset from Mac
docker run \
  -v $(pwd)/data:/app/data \        # read dataset
  -v $(pwd)/outputs:/app/outputs \  # write results
  ml-trainer:v1
```

---

## ⚠️ Important Rules

### 1. Container removal does NOT delete named volumes

```bash
docker rm my-container      # Container gone
docker volume ls            # Volume still there ✅

# You must explicitly remove volumes
docker volume rm ml-logs
# OR remove container AND its volumes together
docker rm -v my-container
```

### 2. Bind mount path must exist on Mac

```bash
# This fails if logs/ doesn't exist
docker run -v $(pwd)/logs:/app/logs volume-demo:v1

# Always create it first
mkdir -p logs
docker run -v $(pwd)/logs:/app/logs volume-demo:v1
```

### 3. Bind mount overwrites container content

```bash
# If /app has files from COPY, and you bind mount $(pwd) to /app
# your local files REPLACE the container files
# Great for dev, dangerous if your local folder is empty!
docker run -v $(pwd):/app my-app   # /app now = whatever is in $(pwd)
```

### 4. Use .dockerignore to avoid copying junk

```
# .dockerignore
logs/
*.log
.env
__pycache__/
.git/
```

---

## 📄 Files

### `app.py` (Logging Demo)

```python
import os
from datetime import datetime

LOG_FILE = "/app/logs/requests.log"
os.makedirs("/app/logs", exist_ok=True)

def log_request(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} — {message}\n")

log_request("Container started")
print("Logged a request. Check logs/requests.log")
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]
```

### `hot-reload/app.py`

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "v1 - change me and refresh!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

---

## 🔧 All Commands in One Place

```bash
# ── Named Volume ─────────────────────────────────────────
docker run -v ml-logs:/app/logs volume-demo:v1
docker volume ls
docker volume inspect ml-logs
docker volume rm ml-logs
docker volume prune                          # Remove all unused

# ── Bind Mount ───────────────────────────────────────────
mkdir -p logs
docker run -v $(pwd)/logs:/app/logs volume-demo:v1
cat logs/requests.log                        # Read from Mac directly

# ── Hot Reload ───────────────────────────────────────────
docker run -p 8080:5000 \
  -v $(pwd):/app \
  --name hot-app \
  hot-reload:v1

# ── Multiple Volumes ─────────────────────────────────────
docker run \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  -v model-cache:/app/models \
  ml-trainer:v1

# ── Read-only Bind Mount (protect your data) ─────────────
docker run -v $(pwd)/data:/app/data:ro my-app
#                                      ↑
#                                  read-only flag
```

---

## 🏋️ Exercises

### Basic
- [ ] Run `volume-demo:v1` **without** volume 3 times — confirm data is lost each time
- [ ] Run with `-v ml-logs:/app/logs` 3 times — confirm all 3 entries persist
- [ ] Run `docker volume ls` and `docker volume inspect ml-logs`

### Intermediate
- [ ] Run with bind mount `$(pwd)/logs:/app/logs` — read `logs/requests.log` directly on Mac
- [ ] Open the logs folder in Finder: `open logs/`
- [ ] Run `docker rm` on the container — confirm the named volume still exists with `docker volume ls`
- [ ] Now run `docker volume rm ml-logs` — confirm it's gone

### Advanced
- [ ] Set up the hot-reload Flask app — edit `app.py` message while container runs, refresh browser
- [ ] Mount a dataset CSV from your Mac into a container and read it with Python
- [ ] Use `:ro` (read-only) flag on a bind mount — try writing from inside container and see it fail
- [ ] **Bonus:** What is the difference between `docker rm -v` and `docker rm`?

### ML-Specific
- [ ] Create a container that writes model training logs to a bind-mounted folder
- [ ] Simulate a dataset pipeline: Mac has `data/input.csv` → container reads it → writes `data/output.csv` back to Mac

---

## 💡 ML Engineer Insight

| ML Workflow | Docker Volume Pattern |
|-------------|----------------------|
| Reading training dataset | `-v $(pwd)/data:/app/data:ro` (read-only) |
| Saving model checkpoints | `-v $(pwd)/checkpoints:/app/checkpoints` |
| Caching HuggingFace models | `-v hf-cache:/root/.cache/huggingface` |
| TensorBoard logs | `-v $(pwd)/runs:/app/runs` |
| Jupyter notebooks | `-v $(pwd)/notebooks:/home/jovyan/work` |

---

## 🔗 Key Takeaways

1. **Containers are stateless by design** — data dies with the container unless mounted
2. **Named volumes** = Docker manages it, survives container removal, good for production
3. **Bind mounts** = You control path, files visible on Mac, perfect for local dev
4. **Hot reload** = bind mount your source code, no rebuild needed during development
5. **`:ro` flag** = protect input data from being accidentally overwritten

---

*Status: 🔄 In Progress*
*Next: Concept 5 — Docker Networking*