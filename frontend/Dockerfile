FROM node:20-bullseye AS deps

WORKDIR /app

COPY app/package*.json ./app/
WORKDIR /app/app
RUN npm ci --ignore-scripts

FROM node:20-bullseye AS builder

WORKDIR /app
COPY . .
COPY --from=deps /app/app/node_modules ./app/node_modules

WORKDIR /app/app
ENV NODE_ENV=production
ARG NUXT_PUBLIC_API_BASE_URL
ENV NUXT_PUBLIC_API_BASE_URL=${NUXT_PUBLIC_API_BASE_URL}
ENV VALUADIS_ENFORCE_PRODUCTION_CONFIG=true
RUN npm run build

FROM node:20-bullseye AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/app/.output ./.output

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

CMD ["node", ".output/server/index.mjs"]
