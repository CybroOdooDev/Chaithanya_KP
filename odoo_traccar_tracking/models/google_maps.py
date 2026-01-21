import requests
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class GoogleMapsAPI:
    """Google Maps API Client for Geolocation and Geocoding"""

    GEOCODING_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    DIRECTIONS_URL = 'https://maps.googleapis.com/maps/api/directions/json'
    DISTANCE_MATRIX_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    def __init__(self, api_key):
        self.api_key = api_key
        self.timeout = 10

    def verify_api_key(self):
        """Verify API key is valid"""
        try:
            params = {
                'latlng': '0,0',
                'key': self.api_key
            }
            response = requests.get(
                self.GEOCODING_URL,
                params=params,
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            _logger.error(f"API verification failed: {str(e)}")
            return False

    def reverse_geocode(self, latitude, longitude):
        """Convert coordinates to address"""
        try:
            params = {
                'latlng': f'{latitude},{longitude}',
                'key': self.api_key
            }
            response = requests.get(
                self.GEOCODING_URL,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    return {
                        'address': data['results'][0]['formatted_address'],
                        'city': self._extract_city(data['results'][0]),
                        'status': 'success'
                    }
            return {'status': 'error', 'address': 'Unknown Location'}
        except Exception as e:
            _logger.error(f"Reverse geocoding error: {str(e)}")
            return {'status': 'error', 'address': 'Unknown Location'}

    def _extract_city(self, result):
        """Extract city from address components"""
        for component in result.get('address_components', []):
            if 'locality' in component['types']:
                return component['long_name']
        return 'Unknown'

    def get_distance(self, origin_lat, origin_lng, dest_lat, dest_lng):
        """Calculate distance between two points"""
        try:
            params = {
                'origins': f'{origin_lat},{origin_lng}',
                'destinations': f'{dest_lat},{dest_lng}',
                'key': self.api_key,
                'units': 'metric'
            }
            response = requests.get(
                self.DISTANCE_MATRIX_URL,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                if data['rows'][0]['elements'][0]['status'] == 'OK':
                    element = data['rows'][0]['elements'][0]
                    return {
                        'distance_m': element['distance']['value'],
                        'distance_km': element['distance']['value'] / 1000,
                        'duration_seconds': element['duration']['value'],
                    }
            return {'distance_m': 0, 'distance_km': 0, 'duration_seconds': 0}
        except Exception as e:
            _logger.error(f"Distance calculation error: {str(e)}")
            return {'distance_m': 0, 'distance_km': 0, 'duration_seconds': 0}

    def get_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
        """Get route between two points"""
        try:
            params = {
                'origin': f'{origin_lat},{origin_lng}',
                'destination': f'{dest_lat},{dest_lng}',
                'key': self.api_key
            }
            response = requests.get(
                self.DIRECTIONS_URL,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            _logger.error(f"Route calculation error: {str(e)}")
            return None
