# Multi-stage Dockerfile for Biomed Chat
FROM python:3.11-slim as base

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Node.js dependencies
RUN npm ci --omit=dev

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create .env from example if it doesn't exist
RUN if [ ! -f .env ]; then cp .env.example .env 2>/dev/null || touch .env; fi

# Expose ports (Node.js on 3000, Python API on 8000)
EXPOSE 3000 8000

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

# Start command
CMD ["npm", "start"]
