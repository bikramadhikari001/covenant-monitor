"""Authentication routes."""
from functools import wraps
from urllib.parse import urlencode
import json
import requests
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, session, redirect, url_for, current_app, render_template, request, flash
from src.auth import requires_auth

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login')
def login():
    """Login route."""
    # Build Auth0 authorize URL
    params = {
        'response_type': 'code',
        'client_id': current_app.config['AUTH0_CLIENT_ID'],
        'redirect_uri': url_for('auth_bp.callback', _external=True),
        'scope': 'openid profile email',
        'audience': current_app.config['AUTH0_AUDIENCE']
    }
    
    # Redirect to Auth0 login page
    auth_url = f"https://{current_app.config['AUTH0_DOMAIN']}/authorize?{urlencode(params)}"
    return redirect(auth_url)

@auth_bp.route('/logout')
def logout():
    """Logout route."""
    # Clear session
    session.clear()
    
    # Build the logout URL
    params = {
        'returnTo': url_for('index', _external=True),
        'client_id': current_app.config['AUTH0_CLIENT_ID']
    }
    
    # Redirect to Auth0 logout endpoint
    return redirect(f"https://{current_app.config['AUTH0_DOMAIN']}/v2/logout?{urlencode(params)}")

@auth_bp.route('/callback')
def callback():
    """Auth0 callback route."""
    # Get the authorization code
    code = request.args.get('code')
    if not code:
        return redirect(url_for('index'))

    # Exchange code for token
    token_url = f"https://{current_app.config['AUTH0_DOMAIN']}/oauth/token"
    token_payload = {
        'grant_type': 'authorization_code',
        'client_id': current_app.config['AUTH0_CLIENT_ID'],
        'client_secret': current_app.config['AUTH0_CLIENT_SECRET'],
        'code': code,
        'redirect_uri': url_for('auth_bp.callback', _external=True)
    }
    
    token_response = requests.post(token_url, json=token_payload)
    token_data = token_response.json()
    
    # Get user info using the access token
    userinfo_url = f"https://{current_app.config['AUTH0_DOMAIN']}/userinfo"
    userinfo_response = requests.get(
        userinfo_url,
        headers={'Authorization': f"Bearer {token_data.get('access_token')}"}
    )
    userinfo = userinfo_response.json()
    
    # Store user info in session
    session['user'] = {
        'name': userinfo.get('name', userinfo.get('nickname', 'User')),
        'userinfo': {
            'email': userinfo.get('email', 'no-email'),
            'picture': userinfo.get('picture'),
            'sub': userinfo.get('sub')
        }
    }
    
    return redirect(url_for('dashboard_bp.dashboard'))

@auth_bp.route('/settings', methods=['GET', 'POST'])
@requires_auth
def settings():
    """User settings/profile route."""
    if request.method == 'POST':
        # Update user information
        user = session['user']
        user['name'] = request.form.get('name', user.get('name', ''))
        user['company'] = request.form.get('company', user.get('company', ''))
        user['role'] = request.form.get('role', user.get('role', ''))
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Create uploads directory if it doesn't exist
                uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(uploads_dir, exist_ok=True)
                
                # Save the file
                filename = secure_filename(f"{user['userinfo']['sub']}.jpg")
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)
                
                # Update user picture URL
                user['userinfo']['picture'] = url_for('static', 
                    filename=f'uploads/profiles/{filename}')
        
        # Update session
        session['user'] = user
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth_bp.settings'))
    
    return render_template('profile.html')
