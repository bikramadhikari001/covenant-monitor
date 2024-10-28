"""Database connection routes."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from src.auth import requires_auth

database_bp = Blueprint('database_bp', __name__)

@database_bp.route('/connections')
@requires_auth
def connections():
    """Show database connections."""
    # Mock data for database connections
    connections = [
        {
            'id': 1,
            'name': 'Production DB',
            'type': 'mysql',
            'host': 'db.example.com',
            'status': 'connected'
        },
        {
            'id': 2,
            'name': 'Test Database',
            'type': 'postgresql',
            'host': 'localhost',
            'status': 'disconnected'
        }
    ]
    return render_template('database/connections.html', connections=connections)

@database_bp.route('/connections/new', methods=['GET', 'POST'])
@requires_auth
def new_connection():
    """Create new database connection."""
    if request.method == 'POST':
        # Mock saving the connection
        flash('Database connection created successfully', 'success')
        return redirect(url_for('database_bp.connections'))
    
    # List of supported database types
    db_types = [
        {'id': 'mysql', 'name': 'MySQL', 'icon': 'database'},
        {'id': 'postgresql', 'name': 'PostgreSQL', 'icon': 'database'},
        {'id': 'sqlserver', 'name': 'SQL Server', 'icon': 'database'},
        {'id': 'oracle', 'name': 'Oracle', 'icon': 'database'},
        {'id': 'mongodb', 'name': 'MongoDB', 'icon': 'database'},
        {'id': 'sqlite', 'name': 'SQLite', 'icon': 'database'}
    ]
    return render_template('database/new_connection.html', db_types=db_types)

@database_bp.route('/connections/<int:connection_id>/test', methods=['POST'])
@requires_auth
def test_connection(connection_id):
    """Test database connection."""
    # Mock testing the connection
    flash('Connection test successful', 'success')
    return redirect(url_for('database_bp.connections'))

@database_bp.route('/connections/<int:connection_id>/delete', methods=['POST'])
@requires_auth
def delete_connection(connection_id):
    """Delete database connection."""
    # Mock deleting the connection
    flash('Connection deleted successfully', 'success')
    return redirect(url_for('database_bp.connections'))
