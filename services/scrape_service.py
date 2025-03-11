from flask import current_app
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import gzip
import pandas as pd
from io import BytesIO
from tqdm import tqdm

BASE_URL = 'http://insideairbnb.com/get-the-data.html'

def scrape():
    with current_app.app_context():
        listings_collection = current_app.db['listings']

        response = requests.get(BASE_URL)
        soup = BeautifulSoup(response.content, 'html.parser')

        h3_tags = soup.find_all('h3')
        h4_tags = soup.find_all('h4')

        # Filter h3_tags to only include "United States"
        filtered_h3_tags = [h3 for h3 in h3_tags if 'United States' in h3.text]
        filtered_h4_tags = [h4 for h3, h4 in zip(h3_tags, h4_tags) if 'United States' in h3.text]

        for h3, h4 in tqdm(zip(filtered_h3_tags, filtered_h4_tags), total=len(filtered_h3_tags)):
            location = h3.text.split(',')
            if len(location) > 3:
                city = ','.join(location[:-2]).strip()
                region = location[-2].strip()
                country = location[-1].strip()
            else:
                city, region, country = [item.strip() for item in location]

            date_str = h4.text.strip()

            # Check if data for this date and location already exists
            existing_listing = listings_collection.find_one({'scrape_date': date_str, 'city': city, 'region': region, 'country': country})
            if existing_listing:
                continue

            table = h3.find_next('table')
            link = table.find('a', href=True)['href']
            if 'listings.csv.gz' in link:
                download_and_save_data(link, city, region, country, date_str, listings_collection)

def download_and_save_data(link, city, region, country, date, listings_collection):
    response = requests.get(link)
    compressed_file = BytesIO(response.content)
    with gzip.open(compressed_file, 'rt') as f:
        df = pd.read_csv(f, low_memory=False)

    for _, row in df.iterrows():
        if pd.isnull(row['name']):
            continue

        listing = {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'host_id': row['host_id'],
            'review_scores_rating': row.get('review_scores_rating'),
            'review_scores_accuracy': row.get('review_scores_accuracy'),
            'review_scores_cleanliness': row.get('review_scores_cleanliness'),
            'review_scores_checkin': row.get('review_scores_checkin'),
            'review_scores_communication': row.get('review_scores_communication'),
            'review_scores_location': row.get('review_scores_location'),
            'review_scores_value': row.get('review_scores_value'),
            'instant_bookable': row.get('instant_bookable'),
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'property_type': row['property_type'],
            'room_type': row['room_type'],
            'accommodates': row['accommodates'],
            'bathrooms': row.get('bathrooms'),
            'bathrooms_text': row.get('bathrooms_text'),
            'bedrooms': row.get('bedrooms'),
            'beds': row.get('beds'),
            'amenities': row['amenities'],
            'price': row['price'],
            'minimum_nights': row['minimum_nights'],
            'maximum_nights': row['maximum_nights'],
            'scrape_date': date,
            'city': city,
            'region': region,
            'country': country
        }
        try:
            listings_collection.insert_one(listing)
        except Exception as e:
            print(f'Error inserting listing: {e}')
