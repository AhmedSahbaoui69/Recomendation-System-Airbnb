import os

class Config:
    DEBUG = True
    TESTING = False
    MONGODB_URI = os.getenv('MONGODB_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
