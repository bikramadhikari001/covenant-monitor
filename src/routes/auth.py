"""Authentication routes."""
from flask import Blueprint, redirect, session, url_for, current_app
from authlib.integrations.flask_client import OAuth
import json

auth_bp = Blueprint('auth_bp', __name__)
oauth = OAuth()

@auth_bp.route('/login')
def login():
    """Handle login request."""
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for('auth_bp.callback', _external=True)
    )

@auth_bp.route('/callback')
def callback():
    """Handle OAuth callback."""
    try:
        token = oauth.auth0.authorize_access_token()
        resp = oauth.auth0.get('userinfo')
        userinfo = resp.json()
        
        # Store the complete token and userinfo in session
        session['user'] = {
            'access_token': token['access_token'],
            'id_token': token['id_token'],
            'userinfo': userinfo,
            'sub': userinfo['sub']  # Add the user ID explicitly
        }
        
        return redirect(url_for('dashboard_bp.dashboard'))
    except Exception as e:
        current_app.logger.error(f"Auth callback error: {str(e)}")
        return redirect(url_for('index'))
