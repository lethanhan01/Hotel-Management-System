import os

# Đường dẫn thư mục gốc của dự án
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'day-la-mot-secret-key-cho-phat-trien-thoi'

class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost:5432/hotel_management'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost:5432/hotel_management'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:admin@localhost:5432/hotel_management'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig # Cấu hình mặc định
}