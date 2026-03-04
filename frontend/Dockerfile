FROM node:20-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire frontend directory structure
COPY . .

# Install dependencies for the actual Nuxt app
WORKDIR /app/app
RUN npm install --force

# Expose port 3020
EXPOSE 3020

# Set environment variables
ENV NUXT_PORT=3020
ENV NUXT_HOST=0.0.0.0
ENV NODE_ENV=development

# Health check for port 3020
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3020/ || exit 1

# Start the Nuxt dev server from the app directory
CMD ["npm", "run", "dev"]
