# ── Stage 1: Builder ──────────────────────────
# Heavy — has node, npm, react-scripts, all build tools
FROM node:18 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY public/ ./public/
COPY src/ ./src/

# Build static files — this is the magic step
RUN npm run build

# ── Stage 2: Production ───────────────────────
# Tiny nginx — just serves the static files
# No Node.js, no npm, no source code in final image

FROM nginx:alpine AS production

# Copy built files from builder into nginx
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

