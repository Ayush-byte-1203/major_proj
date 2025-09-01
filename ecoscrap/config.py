"""
EcoScrap Application - Configuration
====================================

This file contains configuration settings for different environments
(development, testing, production) for the EcoScrap Flask backend.

Configuration includes:
- Database settings and connection strings
- Security settings and session management
- Environment-specific variables and flags
- API configuration and rate limiting
- File upload and storage settings
- Logging configuration and levels

Environment Support:
- Development: Local development with debug mode
- Testing: Test environment with separate database
- Staging: Pre-production environment for testing
- Production: Live production environment with security

Security Features:
- Configurable secret keys
- Session cookie security settings
- CORS configuration for frontend integration
- Rate limiting for API protection

Database Support:
- SQLite (default for development)
- PostgreSQL (production ready)
- MySQL (production ready)
- Environment-based configuration

@author EcoScrap Development Team
@version 1.0.0
@since 2024
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecoscrap-secret-key-2024'
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ecoscrap.db'
    
    # Security configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API configuration
    API_TITLE = 'EcoScrap API'
    API_VERSION = 'v1'
    API_DESCRIPTION = 'Sustainable Scrap Marketplace API'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'ecoscrap.log'

class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Development database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ecoscrap_dev.db'
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    
    # CORS for development
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

class TestingConfig(Config):
    """Testing environment configuration"""
    
    DEBUG = False
    TESTING = True
    
    # Testing database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ecoscrap_test.db'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Testing logging
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production database (use environment variable)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # CORS for production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')

class StagingConfig(Config):
    """Staging environment configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Staging database
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL') or 'sqlite:///ecoscrap_staging.db'
    
    # Staging logging
    LOG_LEVEL = 'INFO'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment variable"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])
