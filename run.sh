#!/bin/bash

# Kill any existing Flask processes
pkill -f flask

# Activate virtual environment
source venv/bin/activate

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Setup database with proper permissions
echo "Setting up database..."
python setup_db.py

# Initialize database tables
echo "Initializing database tables..."
python init_db.py

# Create uploads directory if it doesn't exist
mkdir -p uploads
chmod 775 uploads

# Wait a moment to ensure port is released
sleep 2

# Start the Flask development server
echo "Starting server..."
python -m flask run --host=0.0.0.0 --port=8080
