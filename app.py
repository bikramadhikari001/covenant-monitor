"""Main application module."""
import logging
from datetime import datetime
from flask import Flask, render_template
from src.models.database import db
from src.routes.document import document_bp
from src.routes.dashboard import dashboard_bp
from src.routes.alert import alert_bp
from src.routes.auth import auth_bp, setup_auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def datetime_filter(value):
    """Format datetime."""
    if value is None:
        return ""
    try:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return value

def format_number(value):
    """Format numbers with appropriate suffixes and decimal places."""
    if value is None:
        return ""
    try:
        if isinstance(value, str):
            value = float(value)
        
        # Handle ratios (values between 0 and 10)
        if 0 <= value <= 10:
            return f"{value:.2f}x"
        
        # Handle monetary values
        suffixes = ['', 'K', 'M', 'B', 'T']
        magnitude = 0
        while abs(value) >= 1000 and magnitude < len(suffixes)-1:
            value /= 1000.0
            magnitude += 1
        return f"${value:,.2f}{suffixes[magnitude]}"
    except Exception:
        return value

def create_app():
    """Create Flask application."""
    logger.info("Creating Flask application")
    logger.info("Starting application initialization")
    
    # Create Flask app
    app = Flask(__name__, static_url_path='/static')
    logger.info("Flask app instance created")
    
    # Load configuration
    logger.info("Loading configuration")
    app.config.from_object('config')
    logger.info("Configuration loaded successfully")
    
    # Initialize database
    logger.info("Initializing database")
    db.init_app(app)
    logger.info("Database initialized")
    
    # Initialize Auth0
    setup_auth(app)
    
    # Add template filters
    app.jinja_env.filters['datetime'] = datetime_filter
    app.jinja_env.filters['format_number'] = format_number
    
    # Register blueprints
    logger.info("Registering blueprints")
    
    # Document blueprint
    app.register_blueprint(document_bp)
    logger.info("Imported document blueprint")
    
    # Dashboard blueprint
    app.register_blueprint(dashboard_bp)
    logger.info("Imported dashboard blueprint")
    
    # Alert blueprint
    app.register_blueprint(alert_bp)
    logger.info("Imported alert blueprint")
    
    # Auth blueprint
    app.register_blueprint(auth_bp)
    logger.info("Imported auth blueprint")
    
    logger.info("All blueprints registered successfully")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Index route
    @app.route('/')
    def index():
        """Landing page."""
        logger.info("Handling request to index route")
        return render_template('index.html')
    
    logger.info("Application initialization completed successfully")
    return app

app = create_app()
logger.info("Flask application created successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
