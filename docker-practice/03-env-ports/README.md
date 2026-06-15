# Concept 3 — Environment Variables & Ports 🌐

> Running real containers with config injection and port mapping.
> This is where Docker starts feeling like actual DevOps work.

---

## 📁 Folder Structure

```
03-env-ports/
├── app.py               # Flask API reading from env vars
├── requirements.txt     # flask==3.0.0
├── Dockerfile           # Proper CMD JSON form
└── .env                 # Local env file (never commit this!)
```

---

## 🧠 Core Concepts

### 1. Environment Variables in Docker

Never hardcode config inside your app. Always read from environment:

```python
import os

MODEL_NAME = os.environ.get("MODEL_NAME", "default-model")  # with fallback
APP_ENV    = os.environ.get("APP_ENV", "development")
PORT       = int(os.environ.get("PORT", 5000))
```

**Why this matters for ML:**
- Switch models without rebuilding the image
- Keep API keys out of your code
- Same image runs in dev, staging, and production with different configs

---

### 2. EXPOSE vs Port Mapping

```dockerfile
EXPOSE 5000    # Documentation only — does NOT open the port
```

```bash
docker run -p 8080:5000 my-app   # This actually opens the port
#              ↑     ↑
#          Mac port  Container port
```

> `EXPOSE` is like writing "this door exists" on a blueprint.
> `-p` is actually opening the door.

---

### 3. Why `host="0.0.0.0"` is Required

```python
app.run(host="0.0.0.0", port=5000)
#        ↑
# Accept connections from anywhere
# Without this, Flask only listens inside the container
# and port mapping won't work
```

---

## 📄 Files

### `app.py`

```python
from flask import Flask, jsonify
import os

app = Flask(__name__)

MODEL_NAME = os.environ.get("MODEL_NAME", "default-model")
ENV        = os.environ.get("APP_ENV", "development")
PORT       = int(os.environ.get("PORT", 5000))

@app.route("/")
def home():
    return jsonify({
        "message": "ML Model Server",
        "model": MODEL_NAME,
        "environment": ENV
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

### `.env`

```
MODEL_NAME=bert-base-uncased
APP_ENV=production
PORT=5000
```

> ⚠️ Always add `.env` to `.gitignore` — never commit secrets!

```bash
echo ".env" >> .gitignore
```

---

## 🔧 Key Commands

```bash
# Build
docker build -t ml-server:v1 .

# Run with port mapping
docker run -p 8080:5000 ml-server:v1

# Run with env variables inline
docker run -p 8080:5000 \
  -e MODEL_NAME="bert-base-uncased" \
  -e APP_ENV="production" \
  ml-server:v1

# Run with .env file
docker run -p 8080:5000 --env-file .env --name ml-api ml-server:v1

# Run on different host port
docker run -p 9090:5000 --env-file .env --name ml-api ml-server:v1

# Run in background (detached)
docker run -d -p 8080:5000 --env-file .env --name ml-api ml-server:v1

# View logs
docker logs ml-api
docker logs -f ml-api       # Follow live logs

# Stop and remove
docker stop ml-api
docker rm ml-api
```

---

## ⚠️ Common Mistakes

| Mistake | Fix |
|--------|-----|
| `MODEL_NAME="gpt-2"` in .env | `MODEL_NAME=gpt-2` — no quotes in .env files |
| Flask on `127.0.0.1` | Always use `host="0.0.0.0"` in containers |
| `CMD python app.py` | Always use JSON form: `CMD ["python", "app.py"]` |
| Port already in use error | `docker stop` the old container first |

---

## 🏋️ Exercises

- [x] Build and run, hit `http://localhost:8080` and `/health`
- [x] Run with `-e MODEL_NAME="gpt2"` and confirm response changes
- [x] Create `.env` file and run using `--env-file`
- [x] Run in detached mode, check `docker ps`, view logs
- [x] **Bonus:** Change host port from `8080` to `9090` ✅

---

## 💡 ML Engineer Insight

| ML Workflow | Docker Equivalent |
|-------------|------------------|
| `python train.py --model bert` | `docker run -e MODEL_NAME=bert my-app` |
| Config YAML file | `.env` file with `--env-file` |
| Jupyter on port 8888 | `docker run -p 8888:8888 jupyter` |
| Different configs per experiment | Different `.env` files per run |

---

*Status: ✅ Complete*
*Next: Concept 4 — Volumes & Bind Mounts*