# =========================================================================
# STAGE 1: Build the Svelte SPA static assets
# =========================================================================
FROM node:22-alpine AS builder

# --- CRUCIAL PNPM SUPPLY CHAIN OVERRIDES ---
# Completely disables the age checks and script validation blocks globally
ENV PNPM_CONFIG_MINIMUM_RELEASE_AGE=0
ENV PNPM_CONFIG_VERIFY_DEPS_BEFORE_RUN=false
ENV PNPM_CONFIG_AUDIT=false

# 1. Install pnpm globally inside the build container
RUN npm install -g pnpm

WORKDIR /app

# 2. Copy package descriptors first to take advantage of Docker caching layer
COPY package.json pnpm-lock.yaml* ./

# 3. Install all dependencies (including devDependencies required for building)
RUN pnpm install --frozen-lockfile

# Copy the rest of the source application files
COPY . .

# Run the build natively without policy interference
RUN pnpm build

# =========================================================================
# STAGE 2: Serve the compiled SPA via high-performance Nginx
# =========================================================================
FROM nginx:alpine AS production

# 6. Copy the static files from Stage 1 straight to the Nginx web root folder
COPY --from=builder /app/build /usr/share/nginx/html

# 1. CRUCIAL FIX: Point the output directory env to the main root nginx path
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx

# 7. Copy your custom Nginx routing configuration block
COPY nginx.conf /etc/nginx/templates/nginx.conf.template

CMD ["nginx", "-g", "daemon off;"]
