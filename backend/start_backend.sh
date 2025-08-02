#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start the server
echo "Starting backend server on http://localhost:8000..."
echo "API documentation at http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

# Use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000