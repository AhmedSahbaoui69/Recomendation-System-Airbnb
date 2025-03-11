from flask import Blueprint, request, jsonify
from services.recommendation_service import get_recommendations_service
from flasgger import Swagger, swag_from

recommendation_bp = Blueprint('recommendations_bp', __name__)

@recommendation_bp.route('/recommendations', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string'},
                    'city': {'type': 'string'},
                    'region': {'type': 'string'},
                    'country': {'type': 'string'},
                    'page': {'type': 'integer', 'default': 1},
                    'per_page': {'type': 'integer', 'default': 10}
                },
                'required': ['query', 'city', 'region', 'country']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'A list of recommendations',
            'examples': {
                'application/json': [
                    {'listing_id': '1', 'title': 'Listing 1', 'description': 'Description 1'},
                    {'listing_id': '2', 'title': 'Listing 2', 'description': 'Description 2'}
                ]
            }
        },
        400: {
            'description': 'Bad Request',
            'examples': {
                'application/json': {'error': 'Query parameter is required'}
            }
        }
    }
})
def get_recommendations():
    data = request.get_json() or {}
    # Extract query & location parameters
    query, city, region, country = data.get('query'), data.get('city'), data.get('region'), data.get('country')
    # Extract pagination parameters
    page, per_page = int(data.get('page', 1)), int(data.get('per_page', 10))
    
    # Handle missing parameters
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    if not city or not region or not country:
        return jsonify({"error": "City, region, and country parameters are required"}), 400
    
    recommendations, error = get_recommendations_service(query, city, region, country, page, per_page)

    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(recommendations)