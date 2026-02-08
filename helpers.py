import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import serpapi
import PIL.Image
import requests
from io import BytesIO
import concurrent.futures
from config import SERPAPI_API_KEY

def get_lat_lon(zip_code):
    geolocator = Nominatim(user_agent="menu_lens_app")
    try:
        location = geolocator.geocode(f"{zip_code}, USA")
        return (location.latitude, location.longitude) if location else None
    except: return None

def search_restaurants(query, lat, lon, radius_miles):
    zoom = 15 if radius_miles <= 2 else 13
    params = {
        "engine": "google_maps",
        "q": query,
        "type": "search",
        "ll": f"@{lat},{lon},{zoom}z",
    }
    try:
        client = serpapi.Client(api_key=SERPAPI_API_KEY)
        results = client.search(params)
        places = results.get("local_results", [])
        valid_places = []
        user_coords = (lat, lon)
        for p in places:
            if 'gps_coordinates' in p:
                place_coords = (p['gps_coordinates']['latitude'], p['gps_coordinates']['longitude'])
                distance = geodesic(user_coords, place_coords).miles
                if distance <= radius_miles:
                    p['distance_miles'] = distance
                    p['search_id'] = p.get('data_id', p.get('place_id'))
                    valid_places.append(p)
        valid_places.sort(key=lambda x: x['distance_miles'])
        return valid_places
    except Exception as e:
        return []

def get_menu_photos(search_id):
    params = {
        "engine": "google_maps_photos",
        "data_id": search_id,
    }
    try:
        client = serpapi.Client(api_key=SERPAPI_API_KEY)
        results = client.search(params)
        available_tabs = results.get("categories", [])
        menu_tab_id = None
        for tab in available_tabs:
            if "menu" in tab.get("title", "").lower():
                menu_tab_id = tab.get("id")
                break
        if menu_tab_id:
            params["category_id"] = menu_tab_id
            menu_results = client.search(params)
            return [p.get("image") for p in menu_results.get("photos", [])]
        else:
            return [p.get("image") for p in results.get("photos", [])]
    except: return []

def load_images_parallel(urls):
    def fetch_url(url):
        try:
            response = requests.get(url, timeout=10)
            return PIL.Image.open(BytesIO(response.content))
        except: return None
    target_urls = urls[:10]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_url, target_urls))
    return [img for img in results if img is not None]
