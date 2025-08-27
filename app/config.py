import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    DB_NAME = os.getenv("DB_NAME", "auctionroombooking")
    DB_USER = os.getenv("DB_USER", "flyingcat2003")
    DB_PASS = os.getenv("DB_PASS", "Hanly1912a")
    DB_HOST = os.getenv("DB_HOST", "26.88.139.112")
    DB_PORT = os.getenv("DB_PORT", "5432")
    API_KEY = os.getenv("API_KEY", "supersecret123")
