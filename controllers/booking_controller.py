from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from services.booking_service import book_listing_service
from flasgger import Swagger, swag_from

booking_bp = Blueprint('booking_bp', __name__)

from bson import ObjectId

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = request.headers.get('x-access-token')
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
        
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        # Convert string ID back to ObjectId
        current_user = current_app.db['users'].find_one({'_id': ObjectId(data['user_id'])})
        
        if not current_user:
            return jsonify({'message': 'User not found!'}), 401
            
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired!'}), 401
    except (jwt.InvalidTokenError, KeyError, Exception) as e:
        return jsonify({'message': 'Invalid token!'}), 401
        
    return f(current_user, *args, **kwargs)
  return decorated

@booking_bp.route('/book_listing', methods=['POST'])
@token_required
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'listing_id': {'type': 'string'},
                    'start_date': {'type': 'string', 'format': 'date'},
                    'end_date': {'type': 'string', 'format': 'date'}
                },
                'required': ['listing_id', 'start_date', 'end_date']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Booking successful',
            'examples': {
                'application/json': {'message': 'Booking confirmed'}
            }
        },
        401: {
            'description': 'Unauthorized',
            'examples': {
                'application/json': {'message': 'Token is missing or invalid'}
            }
        }
    }
})
def book_listing(current_user):
    data = request.get_json()
    return book_listing_service(current_user, data)