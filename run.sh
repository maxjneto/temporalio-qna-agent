#!/usr/bin/env bash
# Script to start all project components

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "🚀 Starting Temporal QnA Agent"
echo "======================================"
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your credentials"
    exit 1
fi

# Check if venv exists
if [ ! -d .venv ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python setup.py"
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

echo "✅ Virtual environment activated"
echo

# Cleanup function on exit
cleanup() {
    echo
    echo "🛑 Stopping services..."
    kill 0
}

trap cleanup EXIT

# Start worker in background
echo "🔧 Starting Temporal Worker..."
python worker.py &
WORKER_PID=$!

# Wait for worker to start
sleep 3

# Start API in background
echo "🌐 Starting FastAPI..."
python api/main.py &
API_PID=$!

# Wait for API to start
sleep 3

# Start frontend
echo "🎨 Starting Streamlit..."
streamlit run frontend/app.py

# Wait for processes
wait
