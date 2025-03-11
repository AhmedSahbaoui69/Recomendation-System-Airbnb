from flask import current_app, request, jsonify
import jwt
import numpy as np
from .content_based import generate_content_recommendations
from .collaborative_filtering import generate_collaborative_recommendations

def get_recommendations_service(query, city, region, country, page, per_page):
    listings_collection = current_app.db['listings']
    
    user_mode = False
    user_id = None
    token = request.headers.get('Authorization')
    if token and 'Bearer ' not in token:
      token = None
      
    if token:
        try:
            decoded = jwt.decode(token.split()[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_mode = True
            user_id = decoded['user_id']
        except (jwt.PyJWTError, IndexError):
            pass
    
    listings = list(listings_collection.find({
        'city': city,
        'region': region,
        'country': country
    }))
    
    if not listings:
        return None, "No listings found for the specified location"
    
    try:
        content_result = generate_content_recommendations(listings, query, page, per_page)
    except Exception as e:
        return None, f"Recommendation error: {str(e)}"
    
    for listing_id, embedding in content_result['updates_needed']:
        listings_collection.update_one(
            {'_id': listing_id},
            {'$set': {'embedding': embedding}}
        )
    
    collaborative_scores = {}
    if user_mode:
        user = current_app.db['users'].find_one({'_id': user_id})
        
        # Add null check for user
        if not user:
            current_app.logger.error(f"User {user_id} not found")
            user_mode = False
        else:
            all_users = list(current_app.db['users'].find({}))
            collaborative_recs = generate_collaborative_recommendations(
                user_id,
                user.get('booked_listings', []),
                all_users,
                listings,
                content_result['listing_embeddings']
            )
            collaborative_scores = {rec['listing']['_id']: rec['score'] for rec in collaborative_recs}

    # Use get with default for booked_listings
    alpha = 0.7 if user_mode and len(user.get('booked_listings', [])) > 5 else 0.3

    scored_listings = []
    for listing in listings:
        lid = listing['_id']
        content_score = content_result['scores'].get(lid, 0)
        collaborative_score = collaborative_scores.get(lid, 0)
        hybrid_score = alpha * collaborative_score + (1 - alpha) * content_score
        scored_listings.append((listing, hybrid_score))
    
    scored_listings.sort(key=lambda x: x[1], reverse=True)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_listings = [item[0] for item in scored_listings[start:end]]
    
    formatted_recommendations = [{
        'id': str(l['_id']),
        'name': l['name'],
        'description': l.get('description', '')
    } for l in paginated_listings]
    
    return formatted_recommendations, None