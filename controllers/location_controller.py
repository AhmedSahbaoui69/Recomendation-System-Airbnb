from flask import Blueprint, jsonify, current_app
from flasgger import Swagger, swag_from

location_bp = Blueprint('locations_bp', __name__)

@location_bp.route('/locations', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'A list of locations',
            'examples': {
                'application/json': [
                    {'country': 'Country1', 'region': 'Region1', 'city': 'City1'},
                    {'country': 'Country2', 'region': 'Region2', 'city': 'City2'}
                ]
            }
        }
    }
})
def get_locations():
    db = current_app.db
    locations_collection = db['locations']
    
    # Check if the collection is empty
    if locations_collection.count_documents({}) == 0:
        listings_collection = db['listings']
        listings = listings_collection.find({}, {'_id': 0, 'country': 1, 'region': 1, 'city': 1})
        
        # Extract unique locations from listings
        unique_locations = { 
            (listing['country'], listing['region'], listing['city']) 
            for listing in listings 
        }
        
        # Insert unique locations into the locations collection
        locations_to_insert = [
            {'country': country, 'region': region, 'city': city} 
            for country, region, city in unique_locations
        ]
        locations_collection.insert_many(locations_to_insert)
    
    # Retrieve and return locations
    result = locations_collection.find({}, {'_id': 0, 'country': 1, 'region': 1, 'city': 1})
    locations = list(result)
    return jsonify(locations)
