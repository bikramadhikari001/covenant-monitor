"""Dashboard routes."""
from flask import Blueprint, render_template, session
from src.auth import requires_auth
from src.models.database import Project

dashboard_bp = Blueprint('dashboard_bp', __name__)

def get_user_id():
    """Get user ID from session."""
    if 'user' not in session:
        return None
    return session['user'].get('id', None)

@dashboard_bp.route('/dashboard')
@requires_auth
def dashboard():
    """Display the main dashboard."""
    user_id = get_user_id()
    if user_id:
        projects = Project.query.filter_by(user_id=user_id).all()
    else:
        projects = Project.query.all()  # Show all projects if no user_id
    return render_template('dashboard.html', projects=projects)
