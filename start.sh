#!/bin/bash
set -e

echo "Starting ollama server..."
ollama serve &

echo "Waiting for Ollama to be ready..."
max_attempts=30
attempt=0
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    sleep 2
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "Ollama failed to start. Exiting."
        exit 1
    fi
done
echo "Ollama is ready!"

echo "Pulling model: llama3.2..."
ollama pull llama3.2

echo "Available models:"
ollama list

export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

echo "Starting FastAPI server on port 7860..."
uvicorn app.main:app --host 0.0.0.0 --port 7860