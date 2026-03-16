# Visio-DrawIO Export Skill
# Headless DrawIO export with Visio support

FROM node:18-slim

# Install dependencies for headless rendering
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libxshmfence1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install draw.io CLI
RUN npm install -g @nickvdyck/drawio-cli

# Create app directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci --production

# Copy source
COPY src/ ./src/

# Create work directory
RUN mkdir -p /work

# Set environment
ENV DRAWIO_HEADLESS=true
ENV DISPLAY=:99

WORKDIR /work

# Entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
