FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Find where uv is installed and create a symlink in a standard PATH location
RUN find / -name uv -type f 2>/dev/null | head -1 | xargs -I{} ln -sf {} /usr/local/bin/uv && \
    find / -name uvx -type f 2>/dev/null | head -1 | xargs -I{} ln -sf {} /usr/local/bin/uvx

# Now use uv to install Python
RUN uv python install 3.11 3.12
RUN pip install --no-cache-dir  diagrams

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose ports for Streamlit and health check
EXPOSE 8501 8080

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV HEALTH_CHECK_PORT=8080

# Command to run the application with health check server
CMD ["./start.sh"]
