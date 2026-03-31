#!/bin/bash

# ==========================================
# unified start script for BI360 Application
# ==========================================

# 1. Environment Setup
if [ -d "venv" ]; then
    echo "⚙️  Activating Python virtual environment..."
    source venv/bin/activate
fi

echo "🚀 Starting novoBI360 Package Services..."

# 2. Start GraphQL API Server (FastAPI / Uvicorn)
echo "📦 Starting internal GraphQL API on http://0.0.0.0:8000..."
PYTHONUNBUFFERED=1 uvicorn modules.api:app --host 0.0.0.0 --port 8000 --workers 4 &
API_PID=$!

# Wait briefly for API to bind to port
sleep 3

# 3. Start Dash Dashboard Server (Gunicorn + Gevent)
echo "🌐 Starting Dash UI on http://0.0.0.0:8050..."
cd modules && PYTHONUNBUFFERED=1 gunicorn -w 4 -k gthread --threads 4 app:server -b 0.0.0.0:8050 &
WEB_PID=$!
cd ..

# 4. Graceful Shutdown Handler (Ties both processes to terminal session)
cleanup() {
    echo ""
    echo "🛑 Shutting down novoBI360 Application (API PID: $API_PID, Web PID: $WEB_PID)..."
    kill $API_PID $WEB_PID 2>/dev/null
    wait $API_PID $WEB_PID 2>/dev/null
    echo "✅ Shutdown complete."
    exit 0
}

# Bind cleanup to SIGINT (CTRL+C) and SIGTERM (Kill)
trap cleanup INT TERM EXIT

echo "=========================================================="
echo "✅ BI360 is fully operational!"
echo "➡️  Access the Web Dashboard:  http://localhost:8050/?customer=usiminas"
echo "➡️  Access the GraphQL API:    http://localhost:8000/graphql"
echo "=========================================================="
echo "⚠️  Press CTRL+C to stop both servers safely."

# 5. Keep script running explicitly waiting for user exit
wait $API_PID $WEB_PID
