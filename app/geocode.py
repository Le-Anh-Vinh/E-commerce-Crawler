import time
from geopy.geocoders import Nominatim
from .models import Location

geolocator = Nominatim(user_agent="AirbnbCrawler")

def reverse_geocode(lat, lon) -> Location:
    time.sleep(1)  # avoid rate limit
    location = geolocator.reverse((lat, lon), language='en')
    if not location or 'address' not in location.raw:
        return None
    
    address = location.raw['address']
    full_address = location.address

    # Remove overlapping district/city/country from full address
    for key in ['suburb', 'county', 'city', 'town', 'country']:
        val = address.get(key)
        if val and val in full_address:
            full_address = full_address.replace(val, '').strip(', ')
    
    return Location(
        longitude=lon,
        latitude=lat,
        address=full_address,
        district=address.get('suburb') or address.get('county'),
        city=address.get('city') or address.get('town'),
        country=address.get('country')
    )
