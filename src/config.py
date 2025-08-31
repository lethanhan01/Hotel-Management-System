import os

# Đường dẫn thư mục gốc của dự án
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Prefer environment variable for secret in production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'day-la-mot-secret-key-cho-phat-trien-thoi')

class DevelopmentConfig(Config):
    DEBUG = True
    # Allow overriding database URL via environment variable (e.g. on Vercel)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:admin@localhost:5432/hotel_management'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:admin@localhost:5432/hotel_management'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:admin@localhost:5432/hotel_management'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig  # Cấu hình mặc định
}