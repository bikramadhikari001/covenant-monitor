#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Create instance directory if it doesn't exist
mkdir -p instance

# Initialize database
echo "Creating database..."
python3 -c "from app import create_app; from src.models.database import db; app = create_app(); app.app_context().push(); db.create_all()"

# Run migrations
echo "Running migrations..."
flask db upgrade

echo "Database setup complete!"
