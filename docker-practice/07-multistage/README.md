# Chapter 07 — Multistage Builds 🏗️

> How to build production-grade Docker images that are 10x smaller.
> The technique every DevOps engineer uses before shipping to production.

---

## 📁 Folder Structure

```
07-multistage/
├── app.js                  # Simple Express API
├── package.json
├── Dockerfile.single       # ❌ Single stage — bloated image
├── Dockerfile              # ✅ Multistage — production ready
└── README.md
```

---

## 🧠 The Problem — Single Stage Images Are Huge

Every Dockerfile written before this chapter was a **single stage** build.
One `FROM`, everything baked into one image — including tools you only need to BUILD, not to RUN.

```dockerfile
# Single stage — ships EVERYTHING to production
FROM node:18          # 950MB base with full OS, npm, build tools

WORKDIR /app
COPY package*.json ./
RUN npm install       # node_modules + dev tools
COPY app.js .

CMD ["node", "app.js"]
```

```
What you NEED to run app.js:     What single stage SHIPS:
──────────────────────────       ────────────────────────────
✅ Node.js runtime               ✅ Node.js runtime
✅ node_modules                  ✅ node_modules
✅ app.js                        ✅ app.js
                                 ❌ npm (only needed to install)
                                 ❌ build tools (gcc, make, python)
                                 ❌ full Debian OS
                                 ❌ dev dependencies
```

**Result: ~1.1GB image for a file that's 10 lines long.** 😱

---

## 💡 The Solution — Multistage Builds

Use multiple `FROM` statements. Each is a **stage**.
Docker **throws away** all stages except the last one.
You copy only what you need into the final stage.

```
Stage 1 (builder)              Stage 2 (production)
─────────────────              ────────────────────
node:18 (full)                 node:18-alpine (tiny)
  + npm                          + node_modules  ← copied from Stage 1
  + build tools                  + app.js        ← copied from source
  + node_modules
  + everything

THROWN AWAY after build ❌      This is your final image ✅
```

> Think of it like cooking:
> You use a big messy kitchen (Stage 1) to prep the food.
> You serve only the final dish (Stage 2) to the customer —
> not the kitchen, knives, or packaging.

---

## 📊 Image Size Comparison

| Dockerfile | Base Image | Final Size | Production Ready |
|-----------|------------|------------|-----------------|
| `Dockerfile.single` | `node:18` | ~1.1GB | ❌ |
| `Dockerfile` (multistage) | `node:18-slim` | ~180MB | ✅ |
| `Dockerfile` (alpine) | `node:18-alpine` | ~60MB | ✅ |
| React frontend | `nginx:alpine` | ~25MB | ✅ |

---

## 📄 Files

### `app.js`

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.json({ message: 'Hello from production!' });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

### `Dockerfile.single` ❌ — Single Stage (bad)

```dockerfile
FROM node:18

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY app.js .

EXPOSE 3000
CMD ["node", "app.js"]
```

### `Dockerfile` ✅ — Multistage (good)

```dockerfile
# ── Stage 1: Builder ──────────────────────────────────
# Heavy image — has npm, build tools, everything needed to BUILD
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

# ── Stage 2: Production ───────────────────────────────
# Tiny image — only what's needed to RUN
FROM node:18-alpine AS production

WORKDIR /app

# Copy ONLY what we need from the builder stage
# node_modules are built, not re-installed
COPY --from=builder /app/node_modules ./node_modules
COPY app.js .

EXPOSE 3000
CMD ["node", "app.js"]
```

---

## 🔑 Key Dockerfile Instructions

### `AS` — naming a stage

```dockerfile
FROM node:18 AS builder       # name this stage "builder"
FROM node:18-alpine AS production  # name this stage "production"
```

Names make stages reusable and readable.

### `COPY --from=` — copy from another stage

```dockerfile
# Copy node_modules from builder stage into current stage
COPY --from=builder /app/node_modules ./node_modules

# You can also copy from a public image directly
COPY --from=nginx:alpine /etc/nginx/nginx.conf /etc/nginx/nginx.conf
```

### Base image choices

```
node:18          → Full Debian + Node + npm + build tools  (~950MB)
node:18-slim     → Minimal Debian + Node                   (~200MB)
node:18-alpine   → Alpine Linux + Node                     (~50MB)
nginx:alpine     → Alpine Linux + nginx                    (~7MB)
```

> Alpine is based on musl libc — occasionally causes issues with native modules.
> When in doubt, use `-slim` for safety, `-alpine` for maximum size reduction.

---

## 🔧 Key Commands

```bash
# ── Build ─────────────────────────────────────────────
# Build single stage
docker build -f Dockerfile.single -t single-stage:v1 .

# Build multistage
docker build -t multi-stage:v1 .

# Build specific stage only (useful for debugging)
docker build --target builder -t debug-build .

# ── Compare sizes ──────────────────────────────────────
docker images | grep -E "single|multi|alpine"

# ── Inspect layers ────────────────────────────────────
docker history single-stage:v1
docker history multi-stage:v1

# ── Run ───────────────────────────────────────────────
docker run -p 3000:3000 multi-stage:v1
curl http://localhost:3000

# ── Debug — shell into builder stage ──────────────────
docker build --target builder -t debug .
docker run -it debug sh
# Check what's inside — npm exists here
which npm    # ✅ found
```

---

## 🔍 How to Verify Tools Are Stripped

```bash
# Shell into the final production image
docker run -it multi-stage:v1 sh

# These should NOT exist in production
which npm      # ❌ not found
which npx      # ❌ not found

# This SHOULD exist
which node     # ✅ found
node --version # ✅ v18.x.x

exit
```

This confirms the final image only has what it needs to RUN — nothing else.

---

## 🏋️ Exercises

### Basic
- [x] Build `Dockerfile.single` → check size with `docker images`
- [x] Build `Dockerfile` (multistage) → compare size
- [x] Run multistage version → `curl http://localhost:3000`

### Intermediate
- [x] Run `docker history` on both — compare number of layers
- [x] Build with `--target builder` — shell in and confirm `npm` exists
- [x] Shell into final production image — confirm `npm` does NOT exist

### Advanced
- [ ] Change base image in Stage 2 to `node:18-slim` → compare size vs alpine
- [ ] Add a build argument: `ARG NODE_ENV=production` and use it in the build
- [ ] **Bonus:** Try `FROM node:18-alpine` in Stage 1 too — does it affect final size?

---

## 💡 When to Use Multistage

| Scenario | Use Multistage? |
|----------|----------------|
| React / Vue / Angular frontend | ✅ Always — build then serve with nginx |
| Node.js backend | ✅ Yes — separate install from runtime |
| Python ML model server | ✅ Yes — separate pip install from runtime |
| Simple script / one-off job | ⚠️ Optional — depends on frequency |
| Database (postgres, mongo) | ❌ No — use official images directly |

---

## 🐍 Multistage for Python (ML Engineer Bonus)

Since you're an ML engineer — here's the pattern for Python:

```dockerfile
# Stage 1: Builder — install heavy ML dependencies
FROM python:3.11 AS builder

WORKDIR /app

COPY requirements.txt .

# Install to a specific folder so we can copy it
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Production — slim runtime only
FROM python:3.11-slim AS production

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy model and inference code
COPY src/ ./src/
COPY model/ ./model/

EXPOSE 8000
CMD ["python", "src/serve.py"]
```

```
Without multistage:    With multistage:
────────────────────   ────────────────────
python:3.11 full       python:3.11-slim
+ pip + build tools    + only site-packages
+ gcc for compilation  + your code
~1.5GB ❌             ~400MB ✅
```

---

## 🔗 Key Takeaways

1. **Single stage** ships everything — build tools, dev deps, full OS — waste
2. **Multistage** separates BUILD from RUN — only ships what's needed
3. **`AS name`** labels a stage so you can reference it later
4. **`COPY --from=stage`** pulls specific files from another stage
5. **Alpine** is the smallest base — use for production when possible
6. **`--target`** flag builds only up to a specific stage — great for debugging
7. For **React** — build with Node, serve with nginx. Final image has zero Node.js

---

## 📝 Progress

| Task | Status |
|------|--------|
| Understood single stage problem | ✅ |
| Built multistage Dockerfile | ✅ |
| Compared image sizes | ✅ |
| Verified tools stripped from production | ✅ |
| Applied to fullstack project | ✅ |

---

*Status: ✅ Complete*
*Next: Chapter 08 — Full Stack with Docker Compose + Multistage (mern-admin)*

---

*Part of Docker → DevOps learning journey*
*Platform: macOS · Docker Desktop*
