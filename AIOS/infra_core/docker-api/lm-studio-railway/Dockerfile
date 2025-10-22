# LM Studio Railway Deployment
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    build-essential \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (LM Studio requires it)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Download and install LM Studio
RUN wget https://github.com/janhq/lm-studio/releases/download/v0.2.19/LMStudio-0.2.19-linux.AppImage \
    && chmod +x LMStudio-0.2.19-linux.AppImage

# Create a startup script
RUN echo '#!/bin/bash\n\
export PORT=${PORT:-3000}\n\
export HOST=0.0.0.0\n\
./LMStudio-0.2.19-linux.AppImage --server --port $PORT --host $HOST\n\
' > start-lm-studio.sh && chmod +x start-lm-studio.sh

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-3000}/v1/models || exit 1

# Start LM Studio server
CMD ["./start-lm-studio.sh"]
