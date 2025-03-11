from flask import Blueprint, request
from services.auth_service import login_service, register_service
from flasgger import Swagger, swag_from

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'examples': {
                'application/json': {'token': 'your_jwt_token'}
            }
        },
        401: {
            'description': 'Unauthorized',
            'examples': {
                'application/json': {'message': 'Invalid credentials'}
            }
        }
    }
})
def login():
    data = request.get_json()
    return login_service(data)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'},
                    'email': {'type': 'string'}
                },
                'required': ['username', 'password', 'email']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {
                'application/json': {'message': 'User created'}
            }
        },
        400: {
            'description': 'Bad Request',
            'examples': {
                'application/json': {'message': 'User already exists'}
            }
        }
    }
})
def register():
    data = request.get_json()
    return register_service(data)