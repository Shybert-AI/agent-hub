import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
    OPENCODE_API_URL = os.environ.get('OPENCODE_API_URL', 'http://localhost:8080')
    
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    
    LOG_FILE = 'logs/app.log'
    LOG_LEVEL = 'INFO'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
