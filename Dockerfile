# Base image
FROM python:3.11.9-slim

# Install OS-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps

# Copy the rest of your source code
COPY . .

# Streamlit config (needed for container environments)
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Expose port used by Streamlit
EXPOSE 8501

# Start the Streamlit app
ENTRYPOINT echo "App is running at: http://localhost:8501" && \
           streamlit run app.py --server.port=8501 --server.address=0.0.0.0
