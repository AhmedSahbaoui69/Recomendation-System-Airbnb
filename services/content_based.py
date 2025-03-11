from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def generate_content_recommendations(listings, query_text, page, per_page):
    if not listings:
        return {
            'top_listings': [],
            'scores': {},
            'updates_needed': [],
            'listing_embeddings': {}
        }
    
    # Extract and clean titles
    titles = [str(l.get('description', '')).strip() for l in listings]
    
    # Create TF-IDF vectors
    tfidf = TfidfVectorizer(stop_words='english')
    title_vectors = tfidf.fit_transform(titles).toarray()
    
    # Process query
    query_vector = tfidf.transform([query_text.strip()]).toarray()
    
    # Calculate similarities
    similarities = cosine_similarity(query_vector, title_vectors)[0]
    
    # Prepare embeddings and update tracking
    updates_needed = []
    listing_embeddings = {}
    
    for i, listing in enumerate(listings):
        lid = str(listing['_id'])
        new_embedding = title_vectors[i].tolist()
        listing_embeddings[lid] = new_embedding
        
        # Check if embedding needs update
        current_embedding = listing.get('title_embedding', [])
        if current_embedding != new_embedding:
            updates_needed.append((lid, new_embedding))
    
    # Sort and paginate results
    scored_listings = sorted(
        zip(listings, similarities),
        key=lambda x: x[1],
        reverse=True
    )
    start = (page - 1) * per_page
    end = start + per_page
    paginated = scored_listings[start:end]
    
    return {
        'top_listings': [item[0] for item in paginated],
        'scores': {str(l['_id']): float(s) for l, s in scored_listings},
        'updates_needed': updates_needed,
        'listing_embeddings': listing_embeddings
    }