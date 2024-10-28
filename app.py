"""Main application module."""
import os
from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for
from src.models.database import db
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    logger.info("Starting application initialization")
    
    try:
        app = Flask(__name__)
        logger.info("Flask app instance created")
        
        # Load configuration
        logger.info("Loading configuration")
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///covenant.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        logger.info("Configuration loaded successfully")
        
        # Initialize database
        logger.info("Initializing database")
        db.init_app(app)
        logger.info("Database initialized")
        
        # Register blueprints
        logger.info("Registering blueprints")
        try:
            from src.routes.document import document_bp
            logger.info("Imported document blueprint")
            from src.routes.dashboard import dashboard_bp
            logger.info("Imported dashboard blueprint")
            from src.routes.alert import alert_bp
            logger.info("Imported alert blueprint")
            from src.routes.auth import auth_bp
            logger.info("Imported auth blueprint")
            
            app.register_blueprint(document_bp)
            app.register_blueprint(dashboard_bp)
            app.register_blueprint(alert_bp)
            app.register_blueprint(auth_bp)
            logger.info("All blueprints registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering blueprints: {str(e)}", exc_info=True)
            raise
        
        @app.route('/')
        def index():
            """Home page route."""
            logger.info("Handling request to index route")
            if 'user' in session:
                return redirect(url_for('dashboard_bp.dashboard'))
            return render_template('index.html')
        
        logger.info("Application initialization completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error during app initialization: {str(e)}", exc_info=True)
        raise

# Create the Flask application instance
logger.info("Creating Flask application")
app = create_app()
logger.info("Flask application created successfully")

if __name__ == '__main__':
    app.run(debug=True)
