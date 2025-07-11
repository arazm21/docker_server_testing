#!/bin/bash
set -e

# Check if model folder exists
if [ ! -d "/app/model" ]; then
    echo "Model directory not found. Downloading..."
    python download_model.py
else
    echo "Model directory exists. Skipping download."
fi

# Serve model with mlflow
mlflow models serve -m /app/model -h 0.0.0.0 -p 5000 --env-manager=local
