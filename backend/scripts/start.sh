#!/bin/bash
echo "Seeding database..."
python -m app.seed
echo "Starting backend server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
