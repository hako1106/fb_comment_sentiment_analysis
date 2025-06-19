# --- STAGE 1: BUILD DEPENDENCIES ---
FROM python:3.11-slim-bookworm AS builder

# Install system dependencies for Playwright Chromium and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg build-essential \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxrandr2 \
    libxdamage1 libxfixes3 libasound2 libxshmfence-dev \
    libgbm-dev libgtk-3-0 libglib2.0-0 libgdk-pixbuf2.0-0 \
    libxss1 libxext6 libxrender1 libsm6 libglu1-mesa \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright

# Set workdir and copy requirements
WORKDIR /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium
RUN playwright install --with-deps chromium

# Copy project files
COPY . .

# --- STAGE 2: FINAL IMAGE ---
FROM python:3.11-slim-bookworm

# Install minimal runtime dependencies + curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxrandr2 \
    libxdamage1 libxfixes3 libasound2 libxshmfence-dev \
    libgbm-dev libgtk-3-0 libglib2.0-0 libgdk-pixbuf2.0-0 \
    libxss1 libxext6 libxrender1 libsm6 libglu1-mesa \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID for consistency
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

WORKDIR /app

# Copy installed packages and app files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/share/playwright /usr/local/share/playwright
COPY --from=builder /app /app

# Create directories for Playwright cache with proper permissions
RUN mkdir -p /home/appuser/.cache/ms-playwright && \
    chown -R appuser:appuser /app /home/appuser/.cache

# Switch to non-root user
USER appuser

# Environment variables for Streamlit and Playwright
# Environment variables for Streamlit and Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false \
    MPLCONFIGDIR=/tmp

# Expose port
EXPOSE 8501

# Health check with better configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Use exec form for better signal handling
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Add labels for better container management
LABEL maintainer="thanhngh.ds@gmail.com" \
      version="1.0" \
      description="Vietnamese Facebook Sentiment Analysis App"