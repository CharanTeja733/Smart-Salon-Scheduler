# ---- Builder Stage ----
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for dependency caching
COPY package*.json ./

# Install dependencies (use 'npm ci' if lockfile exists, else 'npm install')
RUN if [ -f package-lock.json ]; then npm ci --only=production; else npm install; fi && \
    npm cache clean --force

# Copy source code
COPY . .

# Build the Vite app (processes Tailwind CSS, JS, etc.)
# Build-time environment variables (VITE_*) must be passed as build args
ARG VITE_API_URL
ARG VITE_STRIPE_PUBLISHABLE_KEY
ARG VITE_GOOGLE_MAPS_API_KEY

ENV VITE_API_URL=$VITE_API_URL \
    VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY \
    VITE_GOOGLE_MAPS_API_KEY=$VITE_GOOGLE_MAPS_API_KEY

RUN npm run build

# ---- Production Stage ----
FROM node:20-alpine AS runner

WORKDIR /app

# Install a tiny static server
RUN npm install -g serve

# Copy built assets from builder
COPY --from=builder /app/dist /app/dist

# Expose the port (serve defaults to 3000, but we set it explicitly)
EXPOSE 3000

# Run serve with SPA support (serves index.html for any unknown route)
CMD ["serve", "-s", "dist", "-l", "3000"]