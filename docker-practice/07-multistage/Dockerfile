# ── Stage 1: builder ────────────────────────────────
# Heavy image ── has npm, build tools, everything
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

# ── Stage 2: Production ───────────────────────────
# Tiny image — only Node runtime, nothing else
FROM node:18-alpine AS production

WORKDIR /app

# Copy ONLY what we need from the builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY app.js .

EXPOSE 3000
CMD ["node", "app.js"]
