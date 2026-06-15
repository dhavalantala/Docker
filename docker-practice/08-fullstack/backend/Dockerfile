# ── Stage 1: Builder ──────────────────────────
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

# ── Stage 2: Production ───────────────────────
FROM node:18-alpine AS production

WORKDIR /app

# Copy only what's needed from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy source
COPY src/ ./src/
COPY package*.json ./

EXPOSE 5000

CMD ["node", "src/index.js"]
