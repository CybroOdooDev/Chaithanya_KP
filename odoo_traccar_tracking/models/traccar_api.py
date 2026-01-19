import requests
import base64
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class TraccarAPI:
    """Traccar API Client"""

    def __init__(self, url, username, password):
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Traccar server"""
        auth_string = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()
        self.session.headers.update({
            'Authorization': f'Basic {auth_string}',
            'Content-Type': 'application/json'
        })

    def test_connection(self):
        """Test connection to Traccar server"""
        try:
            response = self.session.get(
                f"{self.url}/api/server",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            _logger.error(f"Traccar connection error: {str(e)}")
            return False

    def get_devices(self):
        """Get all devices from Traccar"""
        try:
            response = self.session.get(
                f"{self.url}/api/devices",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _logger.error(f"Error fetching devices: {str(e)}")
            return []

    def get_device_location(self, device_id):
        """Get latest location of a device"""
        try:
            response = self.session.get(
                f"{self.url}/api/positions?deviceId={device_id}",
                timeout=10
            )
            response.raise_for_status()
            positions = response.json()
            return positions[0] if positions else None
        except Exception as e:
            _logger.error(f"Error fetching location: {str(e)}")
            return None

    def get_device_history(self, device_id, from_time, to_time):
        """Get location history of a device"""
        try:
            params = {
                'deviceId': device_id,
                'from': from_time.isoformat(),
                'to': to_time.isoformat()
            }
            response = self.session.get(
                f"{self.url}/api/positions",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _logger.error(f"Error fetching history: {str(e)}")
            return []

    def get_device_info(self, device_id):
        """Get device information"""
        try:
            response = self.session.get(
                f"{self.url}/api/devices/{device_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _logger.error(f"Error fetching device info: {str(e)}")
            return None
