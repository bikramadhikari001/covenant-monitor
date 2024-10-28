from flask import Blueprint, render_template, session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create a blueprint for the main routes
main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    """Landing page route."""
    return render_template('index.html')

@main_bp.context_processor
def utility_processor():
    """Add utility functions to template context."""
    def get_alert_count():
        """Get count of active alerts for current user."""
        from src.models.database import Alert
        if 'user' not in session:
            return 0
            
        try:
            return Alert.query.filter_by(
                user_id=session['user'].get('sub'),
                is_active=True
            ).count()
        except Exception as e:
            logger.error(f"Error getting alert count: {str(e)}")
            return 0
    
    return {
        'now': datetime.utcnow(),
        'alert_count': get_alert_count
    }

def init_app(app):
    """Initialize all blueprints."""
    # Import blueprints
    from .auth import auth_bp
    from .document import document_bp
    from .dashboard import dashboard_bp
    from .alert import alert_bp
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from src.models.database import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Register template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format a datetime object."""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('currency')
    def format_currency(value):
        """Format a number as currency."""
        if value is None:
            return '$0.00'
        return f"${value:,.2f}"
    
    @app.template_filter('percentage')
    def format_percentage(value):
        """Format a number as percentage."""
        if value is None:
            return '0%'
        return f"{value:.1f}%"
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(document_bp, url_prefix='/documents')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(alert_bp, url_prefix='/alerts')
    
    # Register context processors
    @app.context_processor
    def inject_user():
        """Inject user info into all templates."""
        return {
            'user': session.get('user', None)
        }
    
    @app.context_processor
    def inject_constants():
        """Inject constants into all templates."""
        return {
            'APP_NAME': 'Covenant Monitor',
            'COMPANY_NAME': 'Your Company',
            'SUPPORT_EMAIL': 'support@example.com'
        }
    
    # Setup before request handlers
    @app.before_request
    def before_request():
        """Actions to perform before each request."""
        from src.models.database import db
        
        # Ensure database connection is active
        if not db.engine.pool.checkedout():
            try:
                db.session.ping()
            except Exception:
                db.session.rollback()
                db.session.remove()
    
    # Setup after request handlers
    @app.after_request
    def after_request(response):
        """Actions to perform after each request."""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # Initialize authentication
    from src.auth import setup_auth
    setup_auth(app)
    
    logger.info("All routes initialized successfully")
    
    return app
