FROM ghcr.io/rmyndharis/openwa:latest

# Set default environment variables
ENV DATABASE_TYPE=sqlite
ENV DATABASE_NAME=/app/data/openwa.sqlite
ENV DATABASE_SYNCHRONIZE=false
ENV ENGINE_TYPE=whatsapp-web.js
ENV SESSION_DATA_PATH=/app/data/sessions
ENV PUPPETEER_HEADLESS=true
ENV PUPPETEER_ARGS="--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage,--disable-gpu"
ENV STORAGE_TYPE=local
ENV STORAGE_LOCAL_PATH=/app/data/media
ENV REDIS_ENABLED=false
ENV WEBHOOK_TIMEOUT=10000
ENV WEBHOOK_MAX_RETRIES=3
ENV WEBHOOK_RETRY_DELAY=5000
ENV RATE_LIMIT_TTL=60
ENV RATE_LIMIT_MAX=100
ENV PLUGINS_ENABLED=true
ENV PLUGINS_DIR=/app/data/plugins

# Copy the startup script
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Use the startup script as the entrypoint
ENTRYPOINT ["/run.sh"]
