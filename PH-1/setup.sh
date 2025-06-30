#!/bin/bash
echo "EXPLAINIUM PH-1 - Quick Setup"

# Check Python
command -v python3 >/dev/null || { echo "Python 3 required"; exit 1; }

# Setup venv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    python3 -m venv env && source env/bin/activate
fi

# Install packages
pip install -r requirements.txt

# Database setup
if command -v psql >/dev/null && pg_isready >/dev/null 2>&1; then
    if createdb docdb 2>/dev/null || psql -d docdb -c "SELECT 1;" >/dev/null 2>&1; then
        export DB_TYPE=postgresql
        echo "Using PostgreSQL"
    else
        echo "PostgreSQL available but database creation failed, falling back to SQLite"
        export DB_TYPE=sqlite
        echo "Using SQLite"
    fi
else
    export DB_TYPE=sqlite
    echo "Using SQLite (PostgreSQL not available)"
fi

# Initialize with explicit DB_TYPE
DB_TYPE=$DB_TYPE python init_db.py || { echo "DB init failed"; exit 1; }
mkdir -p data

echo "🎉 Setup complete!"
echo "Start: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "Web: http://localhost:8000"
echo ""
echo "Starting server automatically..."
echo "Press Ctrl+C to stop the server"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000