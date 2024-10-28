"""Application configuration."""
import os
from datetime import timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key
SECRET_KEY = os.getenv('SECRET_KEY', 'dev')

# Database
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    f'sqlite:///{os.path.join(BASE_DIR, "covenant.db")}'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# File upload
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Auth0 configuration
AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID', 'your-auth0-client-id')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET', 'your-auth0-client-secret')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'your-auth0-domain.auth0.com')
AUTH0_BASE_URL = f'https://{AUTH0_DOMAIN}'
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE', f'https://{AUTH0_DOMAIN}/api/v2/')

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True

# Development configuration
DEBUG = os.getenv('FLASK_ENV') == 'development'
