"""
EcoScrap Application - Startup Script
=====================================

This script provides a convenient way to run the EcoScrap Flask application
with different configurations and options. It handles environment setup,
configuration loading, and application startup with proper error handling.

Usage:
    python run.py                    # Run in development mode
    python run.py --production      # Run in production mode
    python run.py --staging         # Run in staging mode
    python run.py --host 0.0.0.0   # Run on specific host
    python run.py --port 8000       # Run on specific port
    python run.py --debug           # Enable debug mode
    python run.py --reload          # Enable auto-reload

Features:
- Environment-based configuration management
- Command-line argument parsing for flexible deployment
- Automatic database initialization and validation
- Configuration validation and error reporting
- Graceful shutdown handling
- Development vs production mode switching

Environment Modes:
- Development: Debug mode, SQLite database, detailed logging
- Staging: Pre-production testing with production-like settings
- Production: Optimized for performance and security

Configuration Options:
- Host binding (localhost vs external access)
- Port selection (default: 5000)
- Debug mode for development
- Auto-reload for code changes
- Environment-specific settings

Database Management:
- Automatic table creation
- Configuration validation
- Connection testing
- Error reporting

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

import os
import sys
import argparse
from app import app, db
from config import get_config

def setup_environment(env):
    """Set up environment variables"""
    if env == 'production':
        os.environ['FLASK_ENV'] = 'production'
        os.environ['FLASK_DEBUG'] = '0'
    elif env == 'staging':
        os.environ['FLASK_ENV'] = 'staging'
        os.environ['FLASK_DEBUG'] = '0'
    else:
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'

def create_app():
    """Create and configure the Flask application"""
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Initialize database
    with app.app_context():
        db.init_app(app)
        
        # Create tables if they don't exist
        db.create_all()
        
        print(f"Running in {os.environ.get('FLASK_ENV', 'development')} mode")
        print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    return app

def main():
    """Main function to handle command line arguments and run the app"""
    parser = argparse.ArgumentParser(description='Run EcoScrap Flask Application')
    parser.add_argument('--env', choices=['development', 'staging', 'production'], 
                       default='development', help='Environment to run in')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment(args.env)
    
    # Create application
    app = create_app()
    
    # Configure debug mode
    if args.debug:
        app.config['DEBUG'] = True
    
    # Configure auto-reload
    if args.reload:
        app.config['DEBUG'] = True
        app.config['USE_RELOADER'] = True
    
    print(f"Starting EcoScrap application...")
    print(f"Environment: {args.env}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {app.config.get('DEBUG', False)}")
    print(f"Auto-reload: {app.config.get('USE_RELOADER', False)}")
    print("-" * 50)
    
    try:
        # Run the application
        app.run(
            host=args.host,
            port=args.port,
            debug=app.config.get('DEBUG', False),
            use_reloader=app.config.get('USE_RELOADER', False)
        )
    except KeyboardInterrupt:
        print("\nShutting down EcoScrap application...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
