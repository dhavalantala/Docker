# 🐳 Docker Practice Guide — ML Engineer to DevOps

> A structured, hands-on Docker learning path built for engineers coming from a Python/ML background.
> Covers Docker → Docker Compose → Multistage Builds from scratch to production-grade.

---

## 📁 Project Structure

```
docker-practice/
├── 01-basics/                  # Your first Dockerfile
│   ├── app.py
│   └── Dockerfile
│
├── 02-layers/                  # Caching & layer optimization
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile              ✅ Good (cache-friendly)
│   └── Dockerfile.bad          ❌ Bad (cache-busting)
│
├── 03-env-ports/               # Coming next
├── 04-volumes/                 # Coming next
├── 05-docker-compose/          # Phase 2
└── 06-multistage/              # Phase 3
```

---

## 🗺️ Learning Roadmap

### Phase 1 — Docker Core

| # | Concept | Status |
|---|---------|--------|
| 1 | First Dockerfile | ✅ Done |
| 2 | Layers, Caching & Image Size | ✅ Done |
| 3 | Environment Variables & Ports | 🔜 Next |
| 4 | Volumes & Bind Mounts | 🔜 Upcoming |
| 5 | Networking Basics | 🔜 Upcoming |

### Phase 2 — Docker Compose

| # | Concept | Status |
|---|---------|--------|
| 1 | Multi-container apps | 🔜 Upcoming |
| 2 | Services, Networks, Volumes | 🔜 Upcoming |
| 3 | Environment & Overrides | 🔜 Upcoming |

### Phase 3 — Multistage Builds

| # | Concept | Status |
|---|---------|--------|
| 1 | Build vs Runtime separation | 🔜 Upcoming |
| 2 | Production-grade images | 🔜 Upcoming |
| 3 | ML model serving example | 🔜 Upcoming |

---

## 📖 Concepts Covered

### Concept 1 — Your First Dockerfile (`01-basics/`)

**What you learned:**
- `FROM` — choosing a base image
- `WORKDIR` — setting the working directory inside the container
- `COPY` — moving files from host to container
- `CMD` — default command to run on container start

**Key Commands:**
```bash
# Build an image
docker build -t my-first-app .

# Build with a specific tag
docker build -t my-first-app:v2 .

# Run a container
docker run my-first-app

# List all images
docker images
docker images | grep my-first-app
```

**Mental Model:**
```
Dockerfile  →  docker build  →  Image  →  docker run  →  Container
(recipe)                        (cake)                    (slice)
```

---

### Concept 2 — Layers, Caching & Image Size (`02-layers/`)

**What you learned:**
- Every Dockerfile instruction creates a **layer**
- Layers are **cached** — unchanged layers are reused on rebuild
- **Layer order matters** — put rarely-changing things at the top
- Wrong ordering causes `pip install` to re-run on every code change

**The Golden Rule:**
```
Things that change RARELY    ← TOP of Dockerfile
        ↓
Things that change SOMETIMES
        ↓
Things that change OFTEN     ← BOTTOM of Dockerfile
```

**Good vs Bad Pattern:**

```dockerfile
# ❌ BAD — copies all files first, pip install re-runs every time app.py changes
COPY . .
RUN pip install -r requirements.txt

# ✅ GOOD — pip install cached as long as requirements.txt doesn't change
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
```

**Key Commands:**
```bash
# Inspect layers and their sizes
docker history my-first-app:v2

# Build with a specific Dockerfile name
docker build -f Dockerfile.bad -t cache-demo-bad:v1 .

# Compare image sizes
docker images
```

**Why this matters for ML:**
> In ML projects, dependencies like `torch`, `transformers`, or `tensorflow` can be 2–5GB.
> Wrong layer ordering = reinstalling gigabytes on every code change. Always separate deps from code.

---

## 🏋️ Exercises

### Exercise 1 — First Dockerfile
- [x] Modify `app.py` to print your name and date using `datetime`
- [x] Build with tag `my-first-app:v2`
- [x] Verify both images exist with `docker images | grep my-first-app`

### Exercise 2 — Caching
- [ ] Run `docker history cache-demo:v2` and compare with `cache-demo-bad:v1`
- [ ] Add `numpy==1.26.0` to `requirements.txt` — which layers get invalidated?
- [ ] Change only `app.py` after that — confirm `pip install` is still cached

---

## 🔧 Quick Reference — Docker Commands

```bash
# ── Images ──────────────────────────────────────────
docker images                         # List all images
docker pull python:3.11-slim          # Pull image from registry
docker rmi my-app:v1                  # Remove an image
docker image prune                    # Remove dangling images

# ── Build ───────────────────────────────────────────
docker build -t name:tag .            # Build from current directory
docker build -f Dockerfile.prod .     # Build from specific Dockerfile
docker build --no-cache -t name .     # Build without cache

# ── Run & Manage Containers ─────────────────────────
docker run my-app                     # Run a container
docker run -it my-app bash            # Interactive terminal
docker run -d my-app                  # Run in background (detached)
docker run -p 8080:80 my-app          # Map host port 8080 → container port 80
docker run -e MY_VAR=value my-app     # Pass environment variable

# ── Inspect ─────────────────────────────────────────
docker ps                             # List running containers
docker ps -a                          # List all containers (incl. stopped)
docker logs <container_id>            # View container logs
docker exec -it <container_id> bash   # Shell into running container
docker history my-app                 # View image layers

# ── Cleanup ─────────────────────────────────────────
docker stop <container_id>            # Stop a container
docker rm <container_id>              # Remove a container
docker system prune                   # Remove all unused resources
```

---

## 💡 Tips for ML Engineers Moving to DevOps

| ML World | Docker/DevOps Equivalent |
|----------|--------------------------|
| `conda create -n myenv` | `FROM python:3.11-slim` |
| `pip install -r requirements.txt` | `RUN pip install -r requirements.txt` |
| Running `python train.py` | `CMD ["python", "train.py"]` |
| Passing `--config model.yaml` | `ENV` or `CMD` args |
| Sharing a model via Google Drive | Pushing an image to Docker Hub |
| Jupyter notebook | Container with port mapping `-p 8888:8888` |

---

## 🔗 Resources

- [Docker Official Docs](https://docs.docker.com)
- [Docker Hub](https://hub.docker.com) — find base images
- [Play with Docker](https://labs.play-with-docker.com) — free browser playground
- [Dive](https://github.com/wagoodman/dive) — tool to inspect image layers visually

---

## 📝 Progress Log

| Date | Concept | Notes |
|------|---------|-------|
| Day 1 | First Dockerfile | Built my-first-app:v1 and v2 ✅ |
| Day 1 | Layers & Caching | Understood cache invalidation ✅ |
| Day 2 | ENV & Ports | 🔜 |

---

*Guide maintained as part of Docker → DevOps learning journey.*
*Platform: macOS | Docker Desktop*
