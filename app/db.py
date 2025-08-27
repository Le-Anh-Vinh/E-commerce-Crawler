import psycopg2
from .config import Config

def get_connection():
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASS,
        port=Config.DB_PORT
    )
    return conn

def insert_location(cur, loc):
    cur.execute("""
        INSERT INTO "Location" ("Longitude", "Latitude", "LocationAddress", "LocationDistrict", "LocationCity", "LocationCountry")
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT ("Longitude", "Latitude") DO NOTHING
    """, (loc.longitude, loc.latitude, loc.address, loc.district, loc.city, loc.country))

def insert_room(cur, room):
    cur.execute("""
        INSERT INTO "Room" ("RoomName", "RoomDescription", "RoomCapacity", "QuantityOfBed", "RoomRating", "Longitude", "Latitude", "CategoryID", "HostID", "CrawlRoomID")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ("CrawlRoomID") DO NOTHING
        RETURNING "RoomID"
    """, (room.name, room.description, room.capacity, room.beds, room.rating, room.longitude, room.latitude, room.category_id, room.host_id, room.crawl_room_id))
    result = cur.fetchone()
    return result[0] if result else None

def insert_room_image(cur, image_url, room_id):
    cur.execute("""
        INSERT INTO "RoomImage" ("RoomImageURL", "RoomID")
        VALUES (%s, %s)
        ON CONFLICT ("RoomImageURL", "RoomID") DO NOTHING
    """, (image_url, room_id))

def insert_amenity(cur, amenity):
    cur.execute("""
        INSERT INTO "Amenity" ("AName", "ADescription", "AmenityTypeID")
        VALUES (%s, %s, %s)
        ON CONFLICT ("AName") DO NOTHING
    """, (amenity, None, None))

def insert_room_detail(cur, room_id, amenity):
    cur.execute("""
        INSERT INTO "RoomDetail" ("RoomID", "AmenityID", "is_deleted")
        VALUES (%s, (SELECT "AmenityID" FROM "Amenity" WHERE "AName" = %s), false)
        ON CONFLICT ("RoomID", "AmenityID") DO NOTHING
    """, (room_id, amenity))