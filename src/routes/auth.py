"""Authentication routes module."""
from flask import Blueprint, session, redirect, url_for, request, current_app
from functools import wraps
from urllib.parse import urlencode
import logging
import json
from authlib.integrations.flask_client import OAuth
import secrets

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__)
oauth = OAuth()

def setup_auth(app):
    """Setup Auth0."""
    oauth.init_app(app)
    oauth.register(
        "auth0",
        client_id=app.config["AUTH0_CLIENT_ID"],
        client_secret=app.config["AUTH0_CLIENT_SECRET"],
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
    )

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth_bp.login'))
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login')
def login():
    """Login route."""
    session['nonce'] = secrets.token_urlsafe(32)
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for('auth_bp.callback', _external=True),
        nonce=session['nonce']
    )

@auth_bp.route('/callback')
def callback():
    """Auth0 callback route."""
    try:
        token = oauth.auth0.authorize_access_token()
        userinfo = oauth.auth0.userinfo()
        session['user'] = {
            'id': userinfo['sub'],
            'name': userinfo.get('name', ''),
            'email': userinfo.get('email', '')
        }
        logger.info(f"User logged in: {session['user']}")
        return redirect(url_for('dashboard_bp.dashboard'))
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        return redirect(url_for('index'))

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout route."""
    session.clear()
    params = {
        'returnTo': url_for('index', _external=True),
        'client_id': current_app.config['AUTH0_CLIENT_ID']
    }
    return redirect(f'https://{current_app.config["AUTH0_DOMAIN"]}/v2/logout?{urlencode(params)}')
