"""Authentication configuration and utilities."""
from functools import wraps
from flask import session, redirect, url_for, current_app
from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def init_auth(app):
    """Initialize authentication."""
    oauth.init_app(app)
    
    # Configure Auth0
    oauth.register(
        'auth0',
        client_id=app.config['AUTH0_CLIENT_ID'],
        client_secret=app.config['AUTH0_CLIENT_SECRET'],
        api_base_url=f"https://{app.config['AUTH0_DOMAIN']}",
        access_token_url=f"https://{app.config['AUTH0_DOMAIN']}/oauth/token",
        authorize_url=f"https://{app.config['AUTH0_DOMAIN']}/authorize",
        client_kwargs={
            'scope': 'openid profile email',
        },
        server_metadata_url=f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration"
    )
    
    return oauth

def requires_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth_bp.login'))
        
        # Check if user session has the required sub field
        if not session.get('user', {}).get('sub'):
            current_app.logger.error("User session missing sub field")
            session.clear()
            return redirect(url_for('auth_bp.login'))
            
        return f(*args, **kwargs)
    return decorated
