import jwt
from flask import jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

def login_service(data):
    username = data.get('username')
    password = data.get('password')
    
    user = current_app.db['users'].find_one({'username': username})
    
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'user_id': str(user['_id']),
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

def register_service(data):
    username = data.get('username')
    password = data.get('password')
    
    if current_app.db['users'].find_one({'username': username}):
        return jsonify({'message': 'User already exists'}), 400
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    current_app.db['users'].insert_one({
        'username': username,
        'password': hashed_password
    })
    
    return jsonify({'message': 'User registered successfully'}), 201