# 🐳 Docker Complete Cheat Sheet

> A comprehensive reference guide for Docker — from basics to advanced patterns.
> Covers images, containers, networks, volumes, multi-stage builds, and Docker Compose.

---

## Table of Contents

1. [Core Concepts](#1-core-concepts)
2. [Dockerfile — Building Images](#2-dockerfile--building-images)
3. [Building Images](#3-building-images)
4. [Running Containers](#4-running-containers)
5. [Managing Containers](#5-managing-containers)
6. [Networks](#6-networks)
7. [Volumes](#7-volumes)
8. [Multi-Stage Builds](#8-multi-stage-builds)
9. [Docker Compose](#9-docker-compose)
10. [Full Real-World Example — Node.js App](#10-full-real-world-example--nodejs-app)
11. [Essential Commands Quick Reference](#11-essential-commands-quick-reference)

---

## 1. Core Concepts

| Term | What it means |
|------|--------------|
| **Image** | A read-only blueprint/snapshot (like a class in OOP) |
| **Container** | A running instance of an image (like an object from a class) |
| **Dockerfile** | A recipe/script that defines how to build an image |
| **Registry** | A storage hub for images (e.g. Docker Hub, GHCR) |
| **Volume** | Persistent storage that survives container restarts |
| **Network** | A virtual network connecting containers to each other |
| **Docker Compose** | A tool to define and run multi-container applications |

**The basic flow:**

```
Dockerfile  →  docker build  →  Image  →  docker run  →  Container
```

---

## 2. Dockerfile — Building Images

A `Dockerfile` is a plain text file with instructions to build your image, step by step.

### Every Instruction Explained

```dockerfile
# ─── Base Image ────────────────────────────────────────────────
# FROM sets the starting point. Always the first instruction.
# Format: FROM <image>:<tag>
FROM node:20-alpine

# ─── Metadata ──────────────────────────────────────────────────
# LABEL adds key=value metadata to the image.
LABEL maintainer="you@example.com"
LABEL version="1.0"

# ─── Environment Variables ─────────────────────────────────────
# ENV sets environment variables available at build time AND runtime.
ENV NODE_ENV=production
ENV PORT=3000

# ─── Build Arguments ───────────────────────────────────────────
# ARG is only available at build time (not at runtime).
# Pass with: docker build --build-arg APP_VERSION=2.0 .
ARG APP_VERSION=1.0

# ─── Working Directory ─────────────────────────────────────────
# WORKDIR sets the working directory for all subsequent instructions.
# Creates the directory if it doesn't exist.
WORKDIR /app

# ─── Copying Files ─────────────────────────────────────────────
# COPY <src-on-host> <dest-in-image>
# Copy dependency files first to leverage layer caching.
COPY package*.json ./

# ADD is like COPY but also supports:
#   - Extracting tar archives automatically
#   - Downloading from URLs (not recommended — use curl/wget instead)
# Prefer COPY unless you specifically need ADD's extra features.
ADD archive.tar.gz /data/

# ─── Running Commands ──────────────────────────────────────────
# RUN executes a command and creates a new image layer.
# Combine commands with && to reduce the number of layers.
RUN npm ci --only=production \
    && npm cache clean --force

# ─── Exposing Ports ────────────────────────────────────────────
# EXPOSE is documentation only — it does NOT actually publish the port.
# You still need -p when running to publish it to the host.
EXPOSE 3000

# ─── Volumes ───────────────────────────────────────────────────
# VOLUME declares a mount point — data here persists beyond container life.
VOLUME ["/app/data"]

# ─── User ──────────────────────────────────────────────────────
# USER sets which user/group runs the process inside the container.
# Always drop from root for security in production.
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# ─── Copy Remaining Source ─────────────────────────────────────
COPY --chown=appuser:appgroup . .

# ─── Health Check ──────────────────────────────────────────────
# HEALTHCHECK tells Docker how to test that the container is healthy.
# --interval  how often to run (default 30s)
# --timeout   how long to wait for a response (default 30s)
# --retries   how many failures before marking unhealthy (default 3)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

# ─── Entrypoint vs CMD ─────────────────────────────────────────
# ENTRYPOINT — the fixed executable; cannot be overridden (unless --entrypoint flag).
# CMD        — default arguments to ENTRYPOINT, or the default command if no ENTRYPOINT.
#
# Pattern 1: CMD alone (most common for simple images)
CMD ["node", "server.js"]
#
# Pattern 2: ENTRYPOINT + CMD together
# ENTRYPOINT ["node"]
# CMD ["server.js"]          ← user can override just this part
```

### .dockerignore — What to Exclude

Always create a `.dockerignore` file alongside your `Dockerfile` to keep images lean:

```
node_modules
npm-debug.log
.git
.gitignore
*.md
.env
dist
coverage
.DS_Store
```

---

## 3. Building Images

```bash
# Basic build — uses Dockerfile in current directory, tags the image
docker build -t myapp:1.0 .

# Build with a specific Dockerfile path
docker build -f path/to/Dockerfile -t myapp:1.0 .

# Build with build arguments
docker build --build-arg APP_VERSION=2.0 -t myapp:2.0 .

# Build for a specific platform (useful for M1 Macs or cross-compiling)
docker build --platform linux/amd64 -t myapp:1.0 .

# Build and push in one step (BuildKit)
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:1.0 --push .

# View build layers (great for debugging cache)
docker history myapp:1.0

# Remove dangling (untagged) images
docker image prune

# Remove all unused images
docker image prune -a
```

### Layer Caching — The Golden Rule

Docker caches each layer. If a layer hasn't changed, it reuses the cache. **Order instructions from least-to-most frequently changing** to maximise cache hits.

```dockerfile
# ✅ GOOD — dependencies cached separately from source code
COPY package*.json ./        # changes rarely → cached most of the time
RUN npm ci
COPY . .                     # changes often → only this layer rebuilds

# ❌ BAD — every source code change invalidates npm install
COPY . .
RUN npm ci
```

---

## 4. Running Containers

```bash
# Basic run
docker run myapp:1.0

# Run in detached (background) mode
docker run -d myapp:1.0

# Run with a name (easier to reference later)
docker run -d --name my-container myapp:1.0

# Publish port: -p <host-port>:<container-port>
docker run -d -p 8080:3000 myapp:1.0
# Now http://localhost:8080 → container's port 3000

# Publish all EXPOSE'd ports to random host ports
docker run -d -P myapp:1.0

# Set environment variables at runtime
docker run -d -e NODE_ENV=staging -e PORT=4000 myapp:1.0

# Load env vars from a file
docker run -d --env-file .env myapp:1.0

# Mount a volume (named volume)
docker run -d -v mydata:/app/data myapp:1.0

# Mount a bind mount (local directory into container)
docker run -d -v $(pwd)/logs:/app/logs myapp:1.0

# Set resource limits
docker run -d --memory="512m" --cpus="1.0" myapp:1.0

# Run interactively (great for debugging)
docker run -it myapp:1.0 /bin/sh

# Run and auto-remove container when it exits
docker run --rm myapp:1.0

# Restart policies
docker run -d --restart unless-stopped myapp:1.0
# Options: no | always | on-failure | on-failure:3 | unless-stopped

# Connect to a network on startup
docker run -d --network my-network myapp:1.0

# Override the default CMD
docker run myapp:1.0 node migrate.js
```

---

## 5. Managing Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container gracefully (sends SIGTERM, waits, then SIGKILL)
docker stop my-container

# Stop immediately (sends SIGKILL)
docker kill my-container

# Start a stopped container
docker start my-container

# Restart a container
docker restart my-container

# Remove a stopped container
docker rm my-container

# Remove a running container forcefully
docker rm -f my-container

# View logs
docker logs my-container

# Follow (tail) logs in real time
docker logs -f my-container

# Show last 50 lines of logs
docker logs --tail 50 my-container

# Execute a command inside a running container
docker exec my-container ls /app

# Open an interactive shell inside a running container
docker exec -it my-container /bin/sh

# Copy files between host and container
docker cp my-container:/app/logs ./local-logs   # container → host
docker cp ./config.json my-container:/app/       # host → container

# Inspect container details (JSON output)
docker inspect my-container

# View real-time resource usage
docker stats

# View resource usage for one container
docker stats my-container

# View running processes inside a container
docker top my-container
```

---

## 6. Networks

Docker networks allow containers to communicate with each other. By default, each container is isolated.

### Network Types

| Driver | Use Case |
|--------|----------|
| `bridge` | Default for standalone containers on a single host |
| `host` | Container shares the host's network stack (Linux only) |
| `overlay` | Connects containers across multiple Docker hosts (Swarm) |
| `none` | No networking at all |
| `macvlan` | Assigns a real MAC address; container appears as a physical device |

### Network Commands

```bash
# List all networks
docker network ls

# Create a custom bridge network
docker network create my-network

# Create with a specific driver and subnet
docker network create \
  --driver bridge \
  --subnet 172.20.0.0/16 \
  --gateway 172.20.0.1 \
  my-network

# Connect a container to a network
docker network connect my-network my-container

# Disconnect a container from a network
docker network disconnect my-network my-container

# Run a container directly on a network
docker run -d --network my-network --name api myapp:1.0

# Inspect network details
docker network inspect my-network

# Remove a network
docker network rm my-network

# Remove all unused networks
docker network prune
```

### How Container DNS Works

Containers on the same **custom** bridge network can reach each other **by name**:

```bash
# Start a database container on my-network
docker run -d --network my-network --name db postgres:15

# Start an app container on the same network
docker run -d --network my-network --name api myapp:1.0

# Inside 'api', you can reach 'db' just by its container name:
# postgresql://db:5432/mydb
# Docker's internal DNS resolves 'db' → the container's IP automatically
```

> **Note:** This DNS resolution only works on custom networks, NOT on the default `bridge` network.

---

## 7. Volumes

Volumes provide persistent storage. Container filesystems are ephemeral — when a container is removed, its data is gone. Volumes solve this.

### Volume Types

| Type | Syntax | Description |
|------|--------|-------------|
| **Named Volume** | `-v mydata:/app/data` | Managed by Docker, lives in Docker's storage area |
| **Bind Mount** | `-v /host/path:/container/path` | Maps a host directory directly into the container |
| **tmpfs Mount** | `--tmpfs /tmp` | Stored in host memory only, never written to disk |

### Volume Commands

```bash
# Create a named volume
docker volume create mydata

# List all volumes
docker volume ls

# Inspect a volume (find its mount point on the host)
docker volume inspect mydata

# Remove a volume
docker volume rm mydata

# Remove all unused volumes
docker volume prune

# Run a container with a named volume
docker run -d -v mydata:/app/data myapp:1.0

# Run with a bind mount (absolute path required)
docker run -d -v /home/user/project:/app myapp:1.0

# Read-only bind mount
docker run -d -v /home/user/config:/app/config:ro myapp:1.0

# tmpfs (in-memory, good for secrets or temp files)
docker run -d --tmpfs /tmp:rw,size=100m myapp:1.0
```

### When to Use Each

- **Named Volume** → databases, user uploads, anything that needs to persist and be managed by Docker.
- **Bind Mount** → local development (live code reloading), sharing config files from the host.
- **tmpfs** → secrets, session data, anything sensitive that must never touch disk.

---

## 8. Multi-Stage Builds

Multi-stage builds let you use multiple `FROM` statements in one Dockerfile. The trick: **only copy what you need into the final stage**, leaving behind compilers, build tools, and source code. Results in drastically smaller, more secure production images.

### Example — Go Application

```dockerfile
# ── Stage 1: Build ──────────────────────────────────────────────
FROM golang:1.22-alpine AS builder

WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server ./cmd/server

# ── Stage 2: Final (Production) Image ──────────────────────────
FROM scratch
# 'scratch' is an empty image — as small as it gets (no OS, no shell)

COPY --from=builder /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

The builder image might be ~350 MB. The final image will be ~7 MB.

### Example — Node.js Application

```dockerfile
# ── Stage 1: Install all deps (including devDependencies) ───────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# ── Stage 2: Build / compile TypeScript ─────────────────────────
FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ── Stage 3: Production image ───────────────────────────────────
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

COPY --from=build /app/dist ./dist

RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Targeting a Specific Stage

Useful for building a "test" stage in CI without building production:

```bash
# Build only up to the 'build' stage (e.g., to run tests)
docker build --target build -t myapp:test .

# Build the full production image
docker build -t myapp:prod .
```

---

## 9. Docker Compose

Docker Compose defines and runs multi-container applications using a single `compose.yaml` file.

### compose.yaml Structure

```yaml
# compose.yaml

# 'services' defines each container
services:

  # ── Web / App Service ──────────────────────────────────────────
  api:
    # Build from a local Dockerfile
    build:
      context: .               # directory with Dockerfile
      dockerfile: Dockerfile
      args:
        APP_VERSION: "1.0"

    # OR use a pre-built image from a registry
    # image: myapp:1.0

    container_name: my-api     # optional custom name
    ports:
      - "8080:3000"            # host:container
    environment:
      NODE_ENV: production
      DB_HOST: db              # use service name as hostname
      DB_PORT: 5432
    env_file:
      - .env                   # load from a file
    volumes:
      - ./logs:/app/logs       # bind mount
      - uploads:/app/uploads   # named volume
    networks:
      - backend
      - frontend
    depends_on:
      db:
        condition: service_healthy   # wait until db is healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512m
          cpus: "0.5"

  # ── Database Service ───────────────────────────────────────────
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data   # persist DB data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # run on first start
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── Cache Service ──────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redisdata:/data
    networks:
      - backend

  # ── Reverse Proxy ──────────────────────────────────────────────
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - frontend
    depends_on:
      - api

# ── Named Volumes ──────────────────────────────────────────────
volumes:
  pgdata:
  redisdata:
  uploads:

# ── Networks ───────────────────────────────────────────────────
networks:
  backend:
    driver: bridge
  frontend:
    driver: bridge
```

### Docker Compose Commands

```bash
# Start all services (detached)
docker compose up -d

# Build images before starting
docker compose up -d --build

# Scale a specific service to 3 instances
docker compose up -d --scale api=3

# Stop all services (keep containers and volumes)
docker compose stop

# Stop and remove containers, networks (keep volumes)
docker compose down

# Stop, remove containers, networks, AND volumes
docker compose down -v

# View logs for all services
docker compose logs

# Follow logs for a specific service
docker compose logs -f api

# List running services
docker compose ps

# Execute a command in a running service
docker compose exec api /bin/sh

# Run a one-off command (e.g., database migration)
docker compose run --rm api node migrate.js

# Rebuild only a specific service
docker compose build api

# Pull latest images for all services
docker compose pull

# View resource usage
docker compose top
```

### Override Files for Different Environments

```bash
# Default: compose.yaml
# Override for dev: compose.override.yaml  (auto-applied)
# Override for prod: compose.prod.yaml

# Apply a specific override
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

**compose.override.yaml** (development extras, auto-applied):
```yaml
services:
  api:
    build:
      target: dev        # use dev stage from multi-stage Dockerfile
    volumes:
      - .:/app           # live reload — mount source into container
    environment:
      NODE_ENV: development
    command: npm run dev
```

---

## 10. Full Real-World Example — Node.js App

Let's tie everything together with a complete setup.

### Project Structure

```
my-app/
├── src/
│   └── server.js
├── Dockerfile
├── .dockerignore
├── compose.yaml
├── compose.override.yaml
└── .env
```

### Dockerfile (Multi-Stage)

```dockerfile
# ── Stage 1: Development ────────────────────────────────────────
FROM node:20-alpine AS dev
WORKDIR /app
COPY package*.json ./
RUN npm install          # install all deps including devDependencies
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# ── Stage 2: Build ──────────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ── Stage 3: Production ─────────────────────────────────────────
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production

COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

COPY --from=build /app/dist ./dist

RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

### .dockerignore

```
node_modules
dist
.git
.env
*.log
coverage
.DS_Store
```

### compose.yaml (Production)

```yaml
services:
  api:
    build:
      context: .
      target: production
    ports:
      - "3000:3000"
    environment:
      DB_URL: postgresql://myuser:mypassword@db:5432/mydb
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - app-network
    restart: unless-stopped
    volumes:
      - uploads:/app/uploads

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    networks:
      - app-network

volumes:
  pgdata:
  uploads:

networks:
  app-network:
    driver: bridge
```

### compose.override.yaml (Development — auto-applied)

```yaml
services:
  api:
    build:
      target: dev
    volumes:
      - .:/app
      - /app/node_modules   # anonymous volume to preserve container's node_modules
    environment:
      NODE_ENV: development
    command: npm run dev
```

### Step-by-Step Workflow

```bash
# 1. Development — start everything with live reload
docker compose up -d

# 2. Check all services are running
docker compose ps

# 3. Tail the API logs
docker compose logs -f api

# 4. Run database migrations
docker compose exec api node migrate.js

# 5. Open a shell inside the running container
docker compose exec api /bin/sh

# 6. Build for production (target the 'production' stage)
docker build --target production -t myapp:1.0 .

# 7. Push to Docker Hub
docker tag myapp:1.0 yourusername/myapp:1.0
docker push yourusername/myapp:1.0

# 8. Deploy production
docker compose -f compose.yaml up -d

# 9. Tear everything down (remove volumes too)
docker compose down -v
```

---

## 11. Essential Commands Quick Reference

### Images

```bash
docker images                        # list images
docker pull nginx:alpine             # pull from registry
docker push myapp:1.0                # push to registry
docker tag myapp:1.0 myapp:latest    # add a tag
docker rmi myapp:1.0                 # remove image
docker image prune -a                # remove all unused images
docker save myapp:1.0 | gzip > myapp.tar.gz   # export image
docker load < myapp.tar.gz           # import image
```

### Containers

```bash
docker run -d -p 8080:80 --name web nginx    # run container
docker ps                                     # list running
docker ps -a                                  # list all
docker stop web                               # stop
docker start web                              # start
docker restart web                            # restart
docker rm web                                 # remove (must be stopped)
docker rm -f web                              # force remove
docker logs -f web                            # follow logs
docker exec -it web /bin/sh                   # shell into container
docker stats                                  # live resource usage
docker inspect web                            # full details (JSON)
```

### Networks

```bash
docker network ls                             # list networks
docker network create my-net                  # create network
docker network connect my-net web             # connect container
docker network disconnect my-net web          # disconnect container
docker network inspect my-net                 # inspect
docker network rm my-net                      # remove
docker network prune                          # remove unused
```

### Volumes

```bash
docker volume ls                              # list volumes
docker volume create mydata                   # create volume
docker volume inspect mydata                  # inspect
docker volume rm mydata                       # remove
docker volume prune                           # remove unused
```

### System Cleanup

```bash
docker system df                              # disk usage overview
docker system prune                           # remove all unused resources
docker system prune -a --volumes             # nuclear — remove everything unused
```

---

## Tips & Best Practices

- **One process per container** — don't run a database and a web server in the same container.
- **Use specific tags** — prefer `node:20-alpine` over `node:latest` for reproducible builds.
- **Never store secrets in images** — use environment variables, `.env` files, or Docker secrets.
- **Always use `.dockerignore`** — prevents bloated images and accidental secret leaks.
- **Run as non-root** — drop privileges with `USER` for security.
- **Order Dockerfile layers wisely** — stable things first, frequently-changing things last.
- **Use `--no-install-recommends`** for apt installs to keep images lean.
- **Health checks matter** — `depends_on: condition: service_healthy` ensures proper startup order.
- **Prefer multi-stage builds** — separate build dependencies from runtime dependencies.
- **Named volumes > bind mounts in production** — Docker manages them and they're portable.

---

*Generated with ❤️ — A complete Docker reference from zero to production.*