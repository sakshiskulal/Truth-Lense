from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from config.settings import Config
import os

socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for all origins and common headers
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    
    # Initialize SocketIO with deployment-friendly settings
    # Try different async modes based on environment
    async_mode = None
    
    # For production deployment (like Render)
    if os.environ.get('ENVIRONMENT') == 'production':
        try:
            # Try gevent first (most compatible with hosting platforms)
            socketio.init_app(app, cors_allowed_origins="*", async_mode='gevent')
            async_mode = 'gevent'
        except ValueError:
            try:
                # Fallback to threading mode
                socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
                async_mode = 'threading'
            except ValueError:
                # Last resort - let SocketIO choose
                socketio.init_app(app, cors_allowed_origins="*")
                async_mode = 'auto'
    else:
        # For local development
        try:
            socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
            async_mode = 'threading'
        except ValueError:
            socketio.init_app(app, cors_allowed_origins="*")
            async_mode = 'auto'
    
    print(f"SocketIO initialized with async_mode: {async_mode}")
    
    # Register blueprints
    from app.routes.analysis import bp as analysis_bp
    from app.routes.health import bp as health_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.results import bp as results_bp
    
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(results_bp, url_prefix='/api')
    # Register auth under both /api/auth/* and /auth/* with unique names
    app.register_blueprint(auth_bp, url_prefix='/api', name='auth_api')
    # Also expose auth without /api prefix to match current frontend usage
    app.register_blueprint(auth_bp, url_prefix='', name='auth_public')
    
    return app