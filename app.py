"""Main application module."""
import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for
from src.models.database import db
from src.routes.document import document_bp
from src.routes.dashboard import dashboard_bp
from src.routes.alert import alert_bp
from src.routes.auth import auth_bp
from src.auth import requires_auth
from src.data_integration.connector import setup_data_integration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config')
    
    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")
    
    # Register blueprints
    app.register_blueprint(document_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(auth_bp)
    
    # Setup data integration
    setup_data_integration(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/')
    def index():
        """Home page route."""
        # If user is logged in, redirect to dashboard
        if 'user' in session:
            return redirect(url_for('dashboard_bp.dashboard'))
        return render_template('index.html')
    
    @app.template_filter('datetime')
    def format_datetime(value):
        """Format datetime for display."""
        if value is None:
            return ""
        if isinstance(value, str):
            try:
                # Try to parse the string as a datetime
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                try:
                    # Try ISO format
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    return value
        try:
            return value.strftime('%Y-%m-%d %H:%M')
        except (AttributeError, ValueError):
            return str(value)
    
    @app.template_filter('format_number')
    def format_number(value):
        """Format number for display."""
        if value is None:
            return "0"
        try:
            # Convert to float first to handle both int and float
            num = float(value)
            # Check if it's effectively an integer
            if num.is_integer():
                return "{:,.0f}".format(num)
            # Otherwise format with 2 decimal places
            return "{:,.2f}".format(num)
        except (ValueError, TypeError):
            return str(value)
    
    @app.context_processor
    def utility_processor():
        """Add utility functions to template context."""
        return dict(
            now=datetime.utcnow()
        )
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
