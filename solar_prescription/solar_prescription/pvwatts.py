import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (path-safe)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Retrieve the API key from environment variables
API_KEY = os.getenv('NREL_API_KEY')
BASE_URL = 'https://developer.nrel.gov/api/pvwatts/v8.json'

def get_pvwatts_data(system_capacity, module_type, array_type, tilt, azimuth, lat, lon, losses):
    params = {
        'api_key': API_KEY,
        'system_capacity': system_capacity,
        'module_type': module_type,
        'array_type': array_type,
        'tilt': tilt,
        'azimuth': azimuth,
        'lat': lat,
        'lon': lon,
        'losses': losses,
        'format': 'json'
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json(), None  # Return data and no error
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")  # Log the error to the console
        return None, str(e)  # Return no data and the error message
