# Ollama Railway Deployment - Alternative to LM Studio
FROM ollama/ollama:latest

# Set working directory
WORKDIR /app

# Copy model configuration
COPY models.txt .

# Install models on startup
RUN echo '#!/bin/bash\n\
echo "Installing models..."\n\
ollama pull llama3.2:1b-instruct\n\
ollama pull mistral:7b-instruct\n\
echo "Starting Ollama server..."\n\
ollama serve --host 0.0.0.0 --port ${PORT:-11434}\n\
' > start.sh && chmod +x start.sh

# Expose port
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-11434}/api/tags || exit 1

# Start Ollama
CMD ["./start.sh"]
