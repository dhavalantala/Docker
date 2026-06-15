# Chapter 08 — Full Stack 3-Tier App with Docker Compose + Multistage 🐳

> A production-grade 3-tier architecture built from scratch.
> React frontend + Node.js backend + MongoDB database.
> Every Docker concept from Phase 1, 2, and 3 applied in one project.

---

## 📁 Project Structure

```
08-fullstack/
├── backend/
│   ├── src/
│   │   └── index.js            # Express API — CRUD + health check
│   ├── package.json
│   └── Dockerfile              # Multistage — node:18 builder → node:18-alpine
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js            # React entry point
│   │   └── App.js              # UI — add/delete items, calls backend API
│   ├── package.json
│   └── Dockerfile              # Multistage — node:18 builder → nginx:alpine
│
├── docker-compose.yml          # Full stack orchestration
├── .env                        # Environment variables
└── README.md
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     docker compose up                       │
│                                                             │
│  ┌─────────────────┐   ┌─────────────────┐   ┌──────────┐  │
│  │    frontend     │   │    backend      │   │ mongodb  │  │
│  │                 │   │                 │   │          │  │
│  │  React (built)  │──►│  Node.js +      │──►│ mongo:   │  │
│  │  served by      │   │  Express +      │   │ 6.0      │  │
│  │  nginx:alpine   │   │  Mongoose       │   │          │  │
│  │                 │   │  node:18-alpine │   │ volume:  │  │
│  │  port 80        │   │  port 5000      │   │ mongo-   │  │
│  └─────────────────┘   └─────────────────┘   │ data ✅  │  │
│                                               └──────────┘  │
│                    app-network (bridge) ✅                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🐳 Docker Concepts Applied

| Concept | Where it's used | Chapter learned |
|---------|----------------|-----------------|
| Dockerfile + layer caching | `COPY package.json` before `COPY src/` | Ch 02 |
| ENV variables | `MONGO_URI`, `PORT` via environment | Ch 03 |
| Port mapping | `5000:5000`, `80:80` | Ch 03 |
| Named volume | `mongo-data:/data/db` | Ch 04 |
| Custom network | `app-network` bridge | Ch 05 |
| Container DNS | backend connects to `mongodb` by name | Ch 05 |
| Docker Compose | full stack in one file | Ch 06 |
| `depends_on` + healthcheck | backend waits for MongoDB | Ch 06 |
| `restart: unless-stopped` | auto-recovery from crashes | Ch 06 |
| **Multistage builds** | both frontend and backend | **Ch 07** |

---

## 📊 Image Size — Multistage Impact

| Service | Without Multistage | With Multistage | Saving |
|---------|-------------------|-----------------|--------|
| Frontend | ~1.2GB (node:18 + React) | ~92MB (nginx:alpine) | **13x smaller** |
| Backend | ~1.1GB (node:18 full) | ~206MB (node:18-alpine) | **5x smaller** |

---

## 📄 Dockerfiles

### `backend/Dockerfile` — Multistage

```dockerfile
# ── Stage 1: Builder ──────────────────────────────────
# Full Node.js image — has npm, build tools, everything to INSTALL
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

# ── Stage 2: Production ───────────────────────────────
# Tiny Alpine image — only what's needed to RUN
FROM node:18-alpine AS production

WORKDIR /app

# Copy only node_modules from builder — no npm, no build tools
COPY --from=builder /app/node_modules ./node_modules

# Copy source code
COPY src/ ./src/
COPY package*.json ./

EXPOSE 5000
CMD ["node", "src/index.js"]
```

### `frontend/Dockerfile` — Multistage (React → nginx)

```dockerfile
# ── Stage 1: Builder ──────────────────────────────────
# Node.js builds React into static files
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY public/ ./public/
COPY src/ ./src/

# This is the key step — compiles React into plain HTML/CSS/JS
RUN npm run build

# ── Stage 2: Production ───────────────────────────────
# nginx serves the static files — NO Node.js in final image!
FROM nginx:alpine AS production

# Copy built static files from builder into nginx web root
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

> The final frontend image has **zero Node.js**.
> Just nginx + your compiled HTML, CSS, and JS files.

---

## 📄 docker-compose.yml

```yaml
services:

  mongodb:
    image: mongo:6.0
    container_name: mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: fullstack
    volumes:
      - mongo-data:/data/db
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fullstack-backend
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - MONGO_URI=mongodb://admin:password123@mongodb:27017/fullstack?authSource=admin
      - PORT=5000
    networks:
      - app-network
    depends_on:
      mongodb:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: fullstack-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    networks:
      - app-network
    depends_on:
      - backend

networks:
  app-network:
    driver: bridge

volumes:
  mongo-data:
    driver: local
```

---

## ⚙️ Environment Variables

### `.env`

```env
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123
MONGO_DB=fullstack
REACT_APP_API_URL=http://localhost:5000
```

> ⚠️ Never commit `.env` to Git
> `MONGO_URI` uses `authSource=admin` because MongoDB root user lives in the `admin` database

---

## 🚀 How to Run

```bash
# Clone or enter project folder
cd 08-fullstack

# Start full stack — builds all images + starts all containers
docker compose up --build

# Run in background
docker compose up --build -d

# Check all 3 containers are running
docker compose ps
```

Expected output:
```
NAME                 STATUS              PORTS
fullstack-backend    Up                  0.0.0.0:5000->5000/tcp
fullstack-frontend   Up                  0.0.0.0:80->80/tcp
mongodb              Up (healthy)        27017/tcp
```

---

## 🌐 Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:80 | React UI |
| Backend health | http://localhost:5000/health | Health check |
| Get items | http://localhost:5000/items | List all items |
| Create item | POST http://localhost:5000/items | Add new item |
| Delete item | DELETE http://localhost:5000/items/:id | Remove item |

---

## 🧪 Testing with curl

```bash
# Health check
curl http://localhost:5000/health
# {"status":"healthy","service":"backend"}

# Create items
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Learn Docker Multistage"}'

curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Learn Docker Compose"}'

curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Dockerize mern-admin next"}'

# Get all items
curl http://localhost:5000/items

# Delete an item (use _id from GET response)
curl -X DELETE http://localhost:5000/items/<_id>

# Open frontend in browser
open http://localhost:80
```

---

## 🔧 Useful Commands

```bash
# ── Start / Stop ─────────────────────────────────────────
docker compose up --build          # rebuild + start
docker compose up -d               # start in background
docker compose down                # stop + remove containers + network
docker compose down -v             # also removes MongoDB volume (wipes data!)

# ── Logs ─────────────────────────────────────────────────
docker compose logs -f             # follow all services
docker compose logs backend        # backend only
docker compose logs frontend       # frontend only
docker compose logs mongodb        # mongodb only

# ── Debugging ────────────────────────────────────────────
docker compose ps                  # check status + ports
docker compose exec backend sh     # shell into backend
docker compose exec mongodb mongosh # open MongoDB shell
docker compose restart backend     # restart one service

# ── Verify multistage worked ─────────────────────────────
docker compose exec backend sh -c "which npm"   # ❌ not found
docker compose exec backend sh -c "which node"  # ✅ found
docker images | grep fullstack                  # check sizes
```

---

## 🐛 Troubleshooting

### Backend port not accessible
```
curl: (7) Failed to connect to localhost port 5000
```
**Fix:** Check `docker compose ps` — if backend shows `5000/tcp` without `0.0.0.0:`, ports section is missing in `docker-compose.yml`. Add:
```yaml
ports:
  - "5000:5000"
```

### MongoDB auth error
```
Authentication failed — UserNotFound for db "fullstack"
```
**Fix:** Add `?authSource=admin` to `MONGO_URI`:
```
MONGO_URI=mongodb://admin:password123@mongodb:27017/fullstack?authSource=admin
```

### Frontend can't reach backend
```
Failed to fetch — CORS or connection error
```
**Fix:** Make sure `REACT_APP_API_URL=http://localhost:5000` is set before building. React bakes env vars at build time — must rebuild after changing.

### Container name conflict
```
Conflict. The container name already in use
```
**Fix:**
```bash
docker rm -f fullstack-backend fullstack-frontend mongodb
docker compose up --build
```

---

## 💡 Key Learnings

### Why does frontend use nginx in production?
React `npm run build` compiles your JSX/JS into plain static files (HTML, CSS, JS).
These don't need Node.js to serve — any web server works.
nginx is tiny (~7MB), fast, and battle-tested for serving static files.

### Why `--from=builder` in COPY?
Each `FROM` creates a new isolated filesystem.
`COPY --from=builder` reaches back into a previous stage and pulls specific files.
Everything else in that stage is discarded — never ships to production.

### Why `authSource=admin`?
MongoDB creates root users in the `admin` database.
Without `authSource=admin`, MongoDB looks for the user in `fullstack` database — not found.

### Why `depends_on` with `condition: service_healthy`?
Without it, backend starts before MongoDB is ready and crashes immediately.
Healthcheck pings MongoDB every 10s — backend only starts after MongoDB passes.

---

## 🏋️ Exercises

- [x] Build all 3 services with `docker compose up --build`
- [x] Verify all ports with `docker compose ps`
- [x] Test backend health with `curl http://localhost:5000/health`
- [x] Create items via curl and verify in browser
- [ ] Run `docker compose down -v` then `up --build` — confirm data is wiped
- [ ] Run `docker compose down` then `up` — confirm data persists
- [ ] Shell into backend — confirm `npm` doesn't exist in production image
- [ ] **Bonus:** Add a `/items/count` route to backend that returns total item count

---

## 📝 Progress

| Task | Status |
|------|--------|
| Built 3-tier architecture | ✅ |
| Applied multistage to frontend | ✅ |
| Applied multistage to backend | ✅ |
| MongoDB with named volume | ✅ |
| All containers on custom network | ✅ |
| Tested full CRUD via curl | ✅ |
| Opened frontend in browser | ✅ |

---

*Status: ✅ Complete*
*Next: Chapter 09 — Dockerize mern-admin (real world MERN project)*

---

*Part of Docker → DevOps learning journey*
*Stack: React 18 · Node.js 18 · MongoDB 6.0 · nginx · Docker Compose*
*Platform: macOS · Docker Desktop*