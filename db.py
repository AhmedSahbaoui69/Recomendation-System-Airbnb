from pymongo import MongoClient
from flask import current_app

def init_db():
    client = MongoClient(current_app.config['MONGODB_URI'])
    return client['airbnb']
