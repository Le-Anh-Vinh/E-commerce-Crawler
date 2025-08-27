import csv, random, io
from faker import Faker
from .models import Room, Location
from .geocode import reverse_geocode
from .scraper import get_image_urls
from .db import get_connection, insert_location, insert_room, insert_room_image, insert_amenity, insert_room_detail

faker = Faker()

def crawl_and_import_to_postgres(csv_content):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT "CategoryID" FROM "Category"')
    categories = [row[0] for row in cur.fetchall()]

    print("start reading")
    csvfile = io.StringIO(csv_content)  # wrap the string as a file-like object
    reader = csv.DictReader(csvfile)

    print("start crawling")
    count = 0
    for row in reader:
        try:
            location = reverse_geocode(float(row['latitude']), float(row['longitude']))
            images = get_image_urls(row['listing_url'] + "?modal=PHOTO_TOUR_SCROLLABLE")
            amenities = row['amenities'].replace('[', '').replace(']', '').replace('"', '').split(', ') if row['amenities'] else []

            insert_location(cur, location)
            room_id = insert_room(cur, 
                Room(
                    name=row['name'],
                    description=row['description'],
                    capacity=int(row['accommodates'] or 0),
                    beds=int(row['beds'] or 0),
                    rating=float(row['review_scores_rating'] or 0),
                    longitude=float(row['longitude']),
                    latitude=float(row['latitude']),
                    category_id=random.choice(categories),
                    crawl_room_id=int(row['id']),
                    host_id=faker.random_int(min=1, max=19)
                )
            )

            if not room_id:
                continue  # Skip if already exists

            for image_url in images:
                insert_room_image(cur, image_url, room_id)

            for amenity in amenities:
                insert_amenity(cur, amenity)
                insert_room_detail(cur, room_id, amenity)

            conn.commit()
            print(f"Inserted room {row['id']}")

        except Exception as e:
            print(f"Error on row {row.get('id')}: {e}")
            conn.rollback()

        count += 1
        if count >= 40:   # stop after N rows
            break

    cur.close()
    conn.close()
    return "Done"


###########################################################################################################################
# 
###########################################################################################################################


import requests
import csv
from bs4 import BeautifulSoup
from io import BytesIO
import gzip
import json
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "listings_and_reviews.json")

# === State storage ===
def save_listings_and_reviews(data_dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data_dict, f, indent=2, ensure_ascii=False)

def get_listings_and_reviews():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# === Step 1: Get all latest links from InsideAirbnb ===
def fetch_latest_links():
    insideairbnb = requests.get('https://insideairbnb.com/get-the-data/')
    soup = BeautifulSoup(insideairbnb.content, 'html.parser')
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    listings_links = [link for link in links if 'data/listings.csv.gz' in link]
    reviews_links = [link for link in links if 'data/reviews.csv.gz' in link]

    data_dict = {}
    for url in listings_links:
        match = re.match(r"https://data.insideairbnb.com/(.+)/(\d{4}-\d{2}-\d{2})/data/listings\.csv\.gz", url)
        if match:
            city_path, date = match.groups()
            data_dict.setdefault(city_path, {})
            data_dict[city_path]["date"] = date
            data_dict[city_path]["listings"] = url

    for url in reviews_links:
        match = re.match(r"https://data.insideairbnb.com/(.+)/(\d{4}-\d{2}-\d{2})/data/reviews\.csv\.gz", url)
        if match:
            city_path, date = match.groups()
            data_dict.setdefault(city_path, {})
            data_dict[city_path]["date"] = date
            data_dict[city_path]["reviews"] = url
    return data_dict

# === Step 2: Download & extract CSV ===
def download_csv_gz(url):
    resp = requests.get(url)
    resp.raise_for_status()
    with gzip.GzipFile(fileobj=BytesIO(resp.content)) as f:
        content = f.read().decode('utf-8')
    return content  # raw CSV as string

# === Step 3: Process new cities or updates ===
def update_and_crawl():
    old_data = get_listings_and_reviews()
    new_data = fetch_latest_links()

    for city_path, info in new_data.items():
        old_date = old_data.get(city_path, {}).get("date")
        new_date = info.get("date")

        if city_path not in old_data:
            print(f"New city found: {city_path} ({new_date})")
        elif new_date != old_date:
            print(f"Updated data for {city_path}! {old_date} → {new_date}")
        else:
            print(f"No update for {city_path}. Skipping.")
            continue  # skip if nothing changed
          
        # Download CSVs
        listings_csv = download_csv_gz(info["listings"])
        # reviews_csv = download_csv_gz(info["reviews"])

        # TODO: Import these into DB (call your existing import function here)
        crawl_and_import_to_postgres(listings_csv)
        # reviews_importer(reviews_csv)

        # Update JSON state
        old_data[city_path] = info
    
    save_listings_and_reviews(old_data)
    print("Done checking all cities.")

# # Run it
# if __name__ == "__main__":
#     update_and_crawl()











































































# def crawl_and_import_to_postgres(csv_file):
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.execute('SELECT "CategoryID" FROM "Category"')
#     categories = [row[0] for row in cur.fetchall()]

#     with open(csv_file, newline='', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             try:
#                 location = reverse_geocode(float(row['latitude']), float(row['longitude']))
#                 images = get_image_urls(row['listing_url'] + "?modal=PHOTO_TOUR_SCROLLABLE")
#                 amenities = row['amenities'].replace('[', '').replace(']', '').replace('"', '').split(', ') if row['amenities'] else []

#                 insert_location(cur, location)
#                 room_id = insert_room(cur, 
#                     Room(
#                         name=row['name'],
#                         description=row['description'],
#                         capacity=int(row['accommodates'] or 0),
#                         beds=int(row['beds'] or 0),
#                         rating=float(row['review_scores_rating'] or 0),
#                         longitude=float(row['longitude']),
#                         latitude=float(row['latitude']),
#                         category_id=random.choice(categories),
#                         crawl_room_id=int(row['id']),
#                         host_id=faker.random_int(min=1, max=19)
#                     )
#                 )

#                 if not room_id:
#                     continue  # Skip if already exists

#                 for image_url in images:
#                     insert_room_image(cur, image_url, room_id)

#                 for amenity in amenities:
#                     insert_amenity(cur, amenity)
#                     insert_room_detail(cur, room_id, amenity)

#                 conn.commit()

#             except Exception as e:
#                 print(f"Error on row {row.get('id')}: {e}")
#                 conn.rollback()

#     cur.close()
#     conn.close()
#     return "Done"

    