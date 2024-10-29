"""Flask application module."""
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, session, redirect, url_for
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from src.models.database import db
from src.routes.document import document_bp
from src.routes.dashboard import dashboard_bp
from src.routes.alert import alert_bp
from src.routes.auth import auth_bp, oauth
from config import Config

def datetime_filter(value):
    """Format datetime."""
    if value is None:
        return ""
    return value.strftime('%B %d, %Y at %I:%M %p')

def format_number(value):
    """Format number with commas and 2 decimal places."""
    if value is None:
        return ""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return str(value)

def create_app():
    """Create Flask application."""
    print("Creating Flask application")
    print("Starting application initialization")
    
    # Create Flask app instance
    app = Flask(__name__)
    print("Flask app instance created")
    
    # Load configuration
    print("Loading configuration")
    app.config.from_object(Config)
    print("Configuration loaded successfully")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize database
    print("Initializing database")
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        print("Creating database tables")
        db.create_all()
        print("Database tables created")
    
    print("Database initialized")
    
    # Initialize migrations
    Migrate(app, db)
    
    # Register filters
    app.jinja_env.filters['datetime'] = datetime_filter
    app.jinja_env.filters['format_number'] = format_number
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # Initialize OAuth
    oauth.init_app(app)
    with app.app_context():
        oauth.register(
            "auth0",
            client_id=app.config["AUTH0_CLIENT_ID"],
            client_secret=app.config["AUTH0_CLIENT_SECRET"],
            api_base_url=f"https://{app.config['AUTH0_DOMAIN']}",
            access_token_url=f"https://{app.config['AUTH0_DOMAIN']}/oauth/token",
            authorize_url=f"https://{app.config['AUTH0_DOMAIN']}/authorize",
            server_metadata_url=f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid profile email"
            }
        )
    
    # Register blueprints
    print("Registering blueprints")
    
    print("Imported document blueprint")
    app.register_blueprint(document_bp)
    
    print("Imported dashboard blueprint")
    app.register_blueprint(dashboard_bp)
    
    print("Imported alert blueprint")
    app.register_blueprint(alert_bp)
    
    print("Imported auth blueprint")
    app.register_blueprint(auth_bp)
    
    print("All blueprints registered successfully")
    
    @app.route('/')
    def index():
        """Handle request to index route."""
        print("Handling request to index route")
        print(f"Session: {session}")
        return render_template('index.html')
    
    @app.route('/logout')
    def logout():
        """Handle request to logout route."""
        session.clear()
        return redirect(url_for('index'))
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle 500 errors."""
        return render_template('errors/500.html'), 500
    
    print("Application initialization completed successfully")
    return app

app = create_app()

# For local development
if __name__ == '__main__':
    print("Running in development mode")
    app.run(host='0.0.0.0', port=8080, debug=True)
