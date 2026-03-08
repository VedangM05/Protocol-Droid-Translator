#!/bin/bash
# Run BhashaEngine FastAPI backend (from BhashaEngine directory).
cd "$(dirname "$0")"
echo "Starting BhashaEngine API at http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
# Exclude .venv from watch to avoid constant reloads from package file changes
exec .venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000 --reload-exclude '.venv'
