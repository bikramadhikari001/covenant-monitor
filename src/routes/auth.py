"""Authentication routes module."""
from flask import Blueprint, session, redirect, url_for
from functools import wraps
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__)

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/login')
def login():
    """Login route."""
    # For now, just set a mock user session
    session['user'] = {
        'id': '1',
        'name': 'Test User',
        'email': 'test@example.com'
    }
    return redirect(url_for('dashboard_bp.dashboard'))

@auth_bp.route('/logout')
def logout():
    """Logout route."""
    session.clear()
    return redirect(url_for('index'))

@auth_bp.route('/settings')
@login_required
def settings():
    """User settings page."""
    return redirect(url_for('dashboard_bp.dashboard'))
