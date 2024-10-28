#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install pdfplumber openai python-dotenv flask flask-sqlalchemy flask-migrate pandas authlib requests

# Create necessary directories
mkdir -p uploads
mkdir -p instance

# Initialize database
export FLASK_APP=app.py
flask db upgrade

echo "Setup complete!"
