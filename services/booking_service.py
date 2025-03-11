from flask import jsonify, current_app
from bson import ObjectId

def book_listing_service(current_user, data):
    if not current_user or '_id' not in current_user:
        return jsonify({'message': 'Invalid user session'}), 401

    listing_id = data.get('listing_id')
    if not listing_id:
        return jsonify({'message': 'Listing ID is required'}), 400

    # Ensure FIFO order by appending to the array
    current_app.db['users'].update_one(
        {'_id': ObjectId(current_user['_id'])},
        {'$push': {'booked_listings': listing_id}}  # Keeps order intact
    )

    return jsonify({'message': 'Listing booked successfully'}), 200
