# -*- coding: utf-8 -*-

import requests
import json
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TraccarConfig(models.Model):
    _name = 'traccar.config'
    _description = 'Traccar Server Configuration'

    name = fields.Char('Server Name', required=True)
    server_url = fields.Char('Server URL', required=True, help='e.g., http://traccar.example.com:8082')
    username = fields.Char('Username', required=True)
    password = fields.Char('Password', required=True)
    is_active = fields.Boolean('Active', default=True)

    def test_connection(self):
        """Test connection to Traccar server"""
        try:
            url = f"{self.server_url}/api/session"
            response = requests.post(
                url,
                data={'email': self.username, 'password': self.password},
                timeout=5
            )
            if response.status_code == 200:
                return True
            else:
                raise ValidationError(f"Connection failed: {response.status_code}")
        except Exception as e:
            raise ValidationError(f"Connection error: {str(e)}")

    def get_devices(self):
        """Fetch all devices from Traccar"""
        try:
            auth = (self.username, self.password)
            url = f"{self.server_url}/api/devices"
            response = requests.get(url, auth=auth, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                raise ValidationError(f"Failed to fetch devices: {response.status_code}")
        except Exception as e:
            raise ValidationError(f"API Error: {str(e)}")

    def get_device_position(self, device_id):
        """Fetch current position of a device"""
        try:
            auth = (self.username, self.password)
            url = f"{self.server_url}/api/positions"
            params = {'deviceId': device_id}
            response = requests.get(url, auth=auth, params=params, timeout=10)
            if response.status_code == 200:
                positions = response.json()
                return positions[0] if positions else None
            else:
                raise ValidationError(f"Failed to fetch position: {response.status_code}")
        except Exception as e:
            raise ValidationError(f"API Error: {str(e)}")


class FleetVehicleTraccar(models.Model):
    _inherit = 'fleet.vehicle'

    traccar_device_id = fields.Char('Traccar Device ID', help='Unique device ID in Traccar')
    traccar_config_id = fields.Many2one('traccar.config', 'Traccar Server')
    last_latitude = fields.Float('Last Latitude', readonly=True)
    last_longitude = fields.Float('Last Longitude', readonly=True)
    last_update = fields.Datetime('Last Location Update', readonly=True)
    vehicle_speed = fields.Float('Current Speed (km/h)', readonly=True)
    device_battery = fields.Float('Device Battery (%)', readonly=True)

    def fetch_current_location(self):
        """Fetch and update current location from Traccar"""
        for vehicle in self:
            if not vehicle.traccar_device_id or not vehicle.traccar_config_id:
                continue

            try:
                position = vehicle.traccar_config_id.get_device_position(vehicle.traccar_device_id)
                if position:
                    vehicle.write({
                        'last_latitude': position.get('latitude'),
                        'last_longitude': position.get('longitude'),
                        'last_update': position.get('deviceTime'),
                        'vehicle_speed': position.get('speed', 0) * 1.852,  # Convert knots to km/h
                        'device_battery': position.get('attributes', {}).get('battery', 0),
                    })
            except Exception as e:
                _logger.error(f"Error updating location for {vehicle.name}: {str(e)}")

    def fetch_trip_history(self, date_from, date_to):
        """Fetch trip history for a date range"""
        trips = []
        for vehicle in self:
            if not vehicle.traccar_device_id or not vehicle.traccar_config_id:
                continue

            try:
                auth = (vehicle.traccar_config_id.username, vehicle.traccar_config_id.password)
                url = f"{vehicle.traccar_config_id.server_url}/api/reports/trips"
                params = {
                    'deviceId': vehicle.traccar_device_id,
                    'from': date_from,
                    'to': date_to,
                }
                response = requests.get(url, auth=auth, params=params, timeout=10)
                if response.status_code == 200:
                    trips = response.json()
            except Exception as e:
                _logger.error(f"Error fetching trips for {vehicle.name}: {str(e)}")

        return trips