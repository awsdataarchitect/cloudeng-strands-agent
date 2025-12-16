#!/bin/bash

# Startup script for Cloud Engineer Agent
# Runs both Streamlit application and health check server

set -e

echo "Starting Cloud Engineer Agent..."

# Start health check server in the background
echo "Starting health check server on port 8080..."
python health_check.py &
HEALTH_PID=$!

# Give health check server a moment to start
sleep 2

# Check if health check server started successfully
if ! ps -p $HEALTH_PID > /dev/null; then
    echo "ERROR: Health check server failed to start"
    exit 1
fi

echo "Health check server started (PID: $HEALTH_PID)"
echo "Starting Streamlit application on port 8501..."

# Start Streamlit in the foreground
streamlit run app.py

# If Streamlit exits, kill the health check server
kill $HEALTH_PID 2>/dev/null || true
