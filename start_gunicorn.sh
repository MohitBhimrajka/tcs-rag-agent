#!/bin/sh

# Wait a moment for any dependencies to be ready
sleep 2

# Run database migrations automatically on startup
echo "Running database migrations..."
alembic upgrade head || echo "Migration failed or no migrations to run"

# Start the application
echo "Starting Gunicorn..."
gunicorn -c gunicorn/dev.py