"""Configuration module."""
import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///covenant.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Auth0
    AUTH0_CLIENT_ID = 'zEae26bd-e2b5-4e39-ad92-68561f8b2c3f'
    AUTH0_CLIENT_SECRET = 'F0aa7a3d-059f-4670-bbed-dba9f705db29'
    AUTH0_DOMAIN = 'dev-g2tm040xls02bsce.us.auth0.com'
    AUTH0_BASE_URL = f'https://{AUTH0_DOMAIN}'
    AUTH0_AUDIENCE = 'authenticated'
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    
    # Upload config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Cloudinary config
    CLOUDINARY_CLOUD_NAME = "dhynqvbzt"
    CLOUDINARY_API_KEY = "346739971683127"
    CLOUDINARY_API_SECRET = "ZbFLtzXDj8r2_dLoCv6BRnW1E6E"
