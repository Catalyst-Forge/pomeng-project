# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    OPENAI_MODEL_SELECTED = os.getenv('OPENAI_MODEL_SELECTED', '')
    
    # Application
    MODELS_FILE = os.getenv('MODELS_FILE', 'models.json')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'json,txt').split(','))
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
