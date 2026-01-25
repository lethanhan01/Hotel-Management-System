import os

# Đường dẫn thư mục gốc của dự án
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Prefer environment variable for secret in production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'day-la-mot-secret-key-cho-phat-trien-thoi')

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig  # Cấu hình mặc định
}