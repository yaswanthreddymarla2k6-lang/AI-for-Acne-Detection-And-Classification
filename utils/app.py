import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    from routes import auth_bp, api_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Acne Detection API is running'}
    
    return app

def setup_logging(app):
    """Setup application logging"""
    if not app.debug and not app.testing:
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup file handler
        file_handler = RotatingFileHandler(
            'logs/acne_detection.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Acne Detection API startup')

def register_error_handlers(app):
    """Register custom error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'success': False, 'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'success': False, 'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'success': False, 'error': 'Forbidden', 'message': 'Access denied'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'error': 'Not found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'success': False, 'error': 'Method not allowed', 'message': 'HTTP method not allowed'}, 405
    
    @app.errorhandler(413)
    def too_large(error):
        return {'success': False, 'error': 'File too large', 'message': 'Uploaded file is too large'}, 413
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'success': False, 'error': 'Rate limit exceeded', 'message': 'Too many requests'}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'success': False, 'error': 'Internal server error', 'message': 'Something went wrong'}, 500

def register_cli_commands(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        from models import user, detection, setting
        db.create_all()
        print('Database initialized.')
        
        # Create default admin user
        from models.user import User
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@acnedetection.com',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('Default admin user created: admin/admin123')
        
        # Create default settings
        from models.setting import Setting
        default_settings = [
            ('max_file_size', '10485760', 'Maximum file size in bytes (10MB)'),
            ('allowed_file_types', 'jpg,jpeg,png', 'Allowed image file types'),
            ('detection_confidence', '0.5', 'Default detection confidence threshold'),
            ('max_detections_per_image', '50', 'Maximum detections allowed per image'),
            ('maintenance_mode', 'false', 'System maintenance mode'),
            ('api_version', '1.0.0', 'Current API version')
        ]
        
        for key, value, description in default_settings:
            existing = Setting.query.filter_by(key=key).first()
            if not existing:
                setting = Setting(key, value, description)
                db.session.add(setting)
        
        db.session.commit()
        print('Default settings created.')
    
    @app.cli.command()
    def create_user(username, email, password, role='user'):
        """Create a new user."""
        from models.user import User
        
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        print(f'User {username} created successfully.')
    
    @app.cli.command()
    def reset_db():
        """Reset the database."""
        db.drop_all()
        db.create_all()
        print('Database reset.')

# Create application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
