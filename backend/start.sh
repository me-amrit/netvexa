#!/bin/bash
set -e

echo "Starting NETVEXA backend..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# Run database migrations/initialization
echo "Initializing database..."
python -c "import asyncio; from database import init_db; asyncio.run(init_db())"

# Start the application
echo "Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000