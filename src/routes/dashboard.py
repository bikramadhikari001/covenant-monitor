"""Dashboard routes."""
from flask import Blueprint, render_template, session
from src.auth import requires_auth
from src.models.database import Project

dashboard_bp = Blueprint('dashboard_bp', __name__)

def get_user_id():
    """Get user ID from session."""
    if 'user' not in session:
        return 'default'
    return session['user'].get('userinfo', {}).get('email', 'default')

@dashboard_bp.route('/dashboard')
@requires_auth
def dashboard():
    """Display the main dashboard."""
    user_id = get_user_id()
    projects = Project.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', projects=projects)
