"""
Flask performance optimizations for application configurations
"""
import os
from datetime import timedelta

def apply_performance_optimizations(app):
    """Apply performance optimizations to a Flask application"""
    
    # Disable debug mode in production
    app.debug = False
    
    # Enable Jinja2 template compilation cache
    app.jinja_options = {
        'cache_size': 500,
        'auto_reload': False
    }
    
    # Set up server-side session configurations if using Flask-Session
    if 'REDIS_URL' in os.environ:
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = os.environ.get('REDIS_URL')
    else:
        app.config['SESSION_TYPE'] = 'filesystem'
    
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    
    # SQLAlchemy optimizations
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800  # Recycle connections after 30 minutes
    
    # Disable SQLAlchemy event system if not needed
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Add JSON response compressions
    if app.config.get('COMPRESS_ENABLED', True):
        app.config['COMPRESS_MIMETYPES'] = [
            'text/html', 
            'text/css', 
            'text/xml', 
            'application/json', 
            'application/javascript'
        ]
        app.config['COMPRESS_LEVEL'] = 6  # Higher level = better compression but more CPU
        app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress responses larger than this
    
    # Set reasonable limits on uploads if using file uploads
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    
    # Configure cache control for static assets
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=365).total_seconds()
    
    return app
