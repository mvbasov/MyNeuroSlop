# Lightweight CPU-optimized base container image for Python
FROM python:3.10-slim

WORKDIR /app

# Install standard curl library to handle manual debugging or verification loops inside container
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy execution requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy local conversational application server script
COPY chat.py .

# Web service dashboard endpoint port
#EXPOSE 5001

# Default execution context: Starts the unified RAG Flask server dashboard
CMD ["python", "chat.py"]
