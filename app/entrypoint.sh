#!/bin/bash

echo "Starting Redis server..."
redis-server --daemonize yes

echo "Starting FastAPI server..."
fastapi run main.py --port 8000
