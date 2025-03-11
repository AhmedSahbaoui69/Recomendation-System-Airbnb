import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def generate_collaborative_recommendations(user_id, booked_listings, all_users, listings):
    user_ids = [u['_id'] for u in all_users]
    listing_ids = [l['_id'] for l in listings]
    
    user_index = {uid: i for i, uid in enumerate(user_ids)}
    listing_index = {lid: i for i, lid in enumerate(listing_ids)}
    
    user_item = np.zeros((len(user_ids), len(listing_ids)))
    for user in all_users:
        uid = user['_id']
        u_idx = user_index[uid]
        for lid in user.get('booked_listings', []):
            if lid in listing_index:
                user_item[u_idx, listing_index[lid]] = 1
    
    user_sim = cosine_similarity(user_item)
    
    target_idx = user_index.get(user_id)
    if target_idx is None:
        return []
    
    sim_users = [(i, score) for i, score in enumerate(user_sim[target_idx]) if i != target_idx]
    sim_users.sort(key=lambda x: x[1], reverse=True)
    
    seen = set(booked_listings)
    scores = {}
    for i, score in sim_users:
        for lid in all_users[i].get('booked_listings', []):
            if lid not in seen and lid in listing_index:
                scores[lid] = scores.get(lid, 0.0) + score
    
    recommendations = []
    for lid in listing_ids:
        if lid in scores:
            l = next((l for l in listings if l['_id'] == lid), None)
            if l:
                recommendations.append({'listing': l, 'score': scores[lid]})
    
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations