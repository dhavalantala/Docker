# Concept 5 — Docker Networking 🌐

> How containers talk to each other.
> The last concept before Docker Compose — understanding this makes Compose feel obvious.

---

## 📁 Folder Structure

```
05-networking/
├── api.py                  # Flask API — talks to data-service by name
├── data_service.py         # Flask data service — returns model records
├── requirements.txt        # flask, requests
├── Dockerfile.api          # Builds ml-api image
└── Dockerfile.data         # Builds ml-data image
```

---

## 🧠 The Core Problem

By default every container is an **isolated island** — they cannot reach each other.

```
Container A (Flask API)          Container B (Database)
───────────────────              ───────────────────
Wants to call B  ──────────────► ❌ No route to host
```

Docker Networking creates a shared channel between containers.

---

## 🗂️ 3 Network Types

| Type | Flag | Use Case |
|------|------|----------|
| `bridge` | default | containers on same host talking to each other |
| `host` | `--network host` | container shares Mac's network directly |
| `none` | `--network none` | fully isolated, no network at all |

> For local dev and Docker Compose — **bridge is all you need.**

---

## 🔑 Default Bridge vs Custom Bridge

This is the most important distinction in Docker networking.

### Default bridge — containers CANNOT find each other by name

```bash
docker run -d --name app1 python:3.11-slim sleep 3600
docker run -d --name app2 python:3.11-slim sleep 3600

docker exec app2 ping app1
# ❌ ping: app1: Name or service not known
```

Containers are on the same network but DNS doesn't work — only raw IPs work,
and IPs change every run. Useless in practice.

### Custom bridge — containers CAN find each other by name ✅

```bash
docker network create ml-network

docker run -d --name app1 --network ml-network python:3.11-slim sleep 3600
docker run -d --name app2 --network ml-network python:3.11-slim sleep 3600

docker exec app2 python3 -c "
import socket
ip = socket.gethostbyname('app1')
print(f'app1 resolves to: {ip}')
"
# ✅ app1 resolves to: 172.18.0.2
```

**Container name = hostname** on a custom network. Docker handles DNS automatically.

---

## 📄 Files

### `api.py`

```python
from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Talks to data-service container BY NAME — not by IP
DATA_SERVICE_URL = os.environ.get("DATA_SERVICE_URL", "http://data-service:5001")

@app.route("/")
def home():
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/data")
        data = response.json()
        return jsonify({
            "api": "running",
            "data_from_other_container": data
        })
    except Exception as e:
        return jsonify({"api": "running", "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### `data_service.py`

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/data")
def data():
    return jsonify({
        "service": "data-service",
        "records": ["model_v1", "model_v2", "model_v3"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
```

### `Dockerfile.api`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY api.py .
EXPOSE 5000
CMD ["python", "api.py"]
```

### `Dockerfile.data`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY data_service.py .
EXPOSE 5001
CMD ["python", "data_service.py"]
```

---

## 🔧 All Commands

```bash
# ── Networks ─────────────────────────────────────────────
docker network ls                          # list all networks
docker network create ml-network           # create custom bridge network
docker network inspect ml-network          # see containers + IPs on network
docker network rm ml-network               # remove network
docker network connect ml-network <name>   # add running container to network
docker network disconnect ml-network <name># remove container from network

# ── Build ────────────────────────────────────────────────
docker build -f Dockerfile.api -t ml-api:v1 .
docker build -f Dockerfile.data -t ml-data:v1 .

# ── Run on custom network ────────────────────────────────
docker run -d --name data-service --network ml-network ml-data:v1
docker run -d --name ml-api --network ml-network -p 8080:5000 ml-api:v1

# ── Test ─────────────────────────────────────────────────
curl http://localhost:8080

# ── Cleanup ──────────────────────────────────────────────
docker stop ml-api data-service
docker rm ml-api data-service
docker network rm ml-network
```

---

## 🔍 How Docker DNS Works

When you create a custom network, Docker runs an internal DNS server.

```
ml-api container wants to reach data-service

1. api.py calls → http://data-service:5001/data
                        ↓
2. Docker DNS resolves "data-service" → 172.18.0.2
                        ↓
3. Request reaches data_service container
                        ↓
4. Response comes back to ml-api ✅
```

The container NAME is the hostname. That's why naming matters.

---

## ⚠️ Common Mistakes

| Mistake | Fix |
|--------|-----|
| Containers can't find each other by name | Use a custom network, not the default bridge |
| `ping` not found in slim images | Use `python3 -c "import socket; socket.gethostbyname('name')"` to test DNS |
| `Conflict. container name already in use` | `docker stop` doesn't remove — also run `docker rm`, or use `--rm` flag |
| Network not found | Run `docker network create` before `docker run` |
| Forgot `--network` flag | Container joins default bridge — can't reach named containers |

---

## 🏋️ Exercises

- [x] Run `docker network ls` — see default networks (bridge, host, none)
- [x] Create `ml-network` and verify with `docker network ls`
- [x] Start `app1` and `app2` on `ml-network`, test DNS with Python socket
- [x] Build and run both Flask services on `ml-network`
- [x] Hit `curl http://localhost:8080` — API fetches data from other container ✅
- [ ] Run `docker network inspect ml-network` — find both container IPs
- [ ] **Bonus:** Stop `data-service` and hit the API — what error appears?

---

## 💡 Lessons Learned from Debugging

| Error seen | What it taught |
|-----------|----------------|
| `ping: not found` in slim image | Slim images have no extras — use Python to debug networking |
| `Conflict. container name in use` | `docker stop` ≠ `docker rm` — stopped containers still exist |
| `no such file or directory` for Dockerfile | Always run `ls` first to confirm files exist before building |

---

## 💡 ML Engineer Insight

| ML Workflow | Docker Network Pattern |
|-------------|----------------------|
| Model server + feature store | Two containers on same custom network |
| API gateway + inference service | `--name inference` → call by name from gateway |
| Training job + metrics server | Both on `ml-network`, metrics pulls from trainer |
| Multiple microservices | All on one custom network, talk by container name |

---

## 🔗 Key Takeaways

1. **Default bridge** — containers cannot find each other by name ❌
2. **Custom bridge** — container name = hostname, DNS works automatically ✅
3. **Always name your containers** — `--name` makes networking predictable
4. **`docker stop` ≠ `docker rm`** — stop pauses, rm removes
5. **This is exactly what Docker Compose does for you** — auto-creates a network, auto-assigns names

---

*Status: ✅ Complete*
*Next: Docker Compose — all concepts in one file 🚀*
