from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)


class TraccarConnection(models.Model):
    _name = 'traccar.connection'
    _description = 'Traccar Server Connection'
    _rec_name = 'server_url'

    server_url = fields.Char(
        string='Server URL',
        required=True,
        help='Traccar server URL (e.g., https://traccar.example.com:8082)'
    )
    username = fields.Char(
        string='Username',
        required=True,
        help='Traccar admin username'
    )
    password = fields.Char(
        string='Password',
        required=True,
        help='Traccar admin password'
    )
    google_maps_api = fields.Char(
        string='Google Maps API Key',
        help='Google Maps API Key for geocoding and map display'
    )
    is_active = fields.Boolean(
        string='Active',
        default=True
    )
    last_sync = fields.Datetime(
        string='Last Sync',
        readonly=True
    )
    sync_frequency = fields.Integer(
        string='Sync Frequency (minutes)',
        default=5,
        help='How often to sync with Traccar server'
    )

    _sql_constraints = [
        ('unique_url', 'unique(server_url)', 'Server URL must be unique!'),
    ]

    @api.constrains('server_url')
    def _check_url(self):
        for record in self:
            if not record.server_url.startswith(('http://', 'https://')):
                raise ValidationError('Server URL must start with http:// or https://')

    def test_connection(self):
        """Test connection to Traccar server"""
        self.ensure_one()
        try:
            response = requests.get(
                f"{self.server_url}/api/devices",
                auth=(self.username, self.password),
                timeout=10
            )
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Connection to Traccar server successful!',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise ValidationError(f'Connection failed: {response.status_code}')
        except Exception as e:
            raise ValidationError(f'Connection error: {str(e)}')

    def sync_devices(self):
        """Sync devices from Traccar"""
        self.ensure_one()
        try:
            response = requests.get(
                f"{self.server_url}/api/devices",
                auth=(self.username, self.password),
                timeout=10
            )
            if response.status_code == 200:
                devices = response.json()
                device_obj = self.env['traccar.device']

                for device in devices:
                    existing = device_obj.search([('device_id', '=', device.get('id'))])
                    if not existing:
                        device_obj.create({
                            'name': device.get('name'),
                            'device_id': device.get('id'),
                            'connection_id': self.id,
                            'unique_id': device.get('uniqueId'),
                        })

                self.last_sync = fields.Datetime.now()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': f'Synced {len(devices)} devices from Traccar',
                        'type': 'success',
                        'sticky': False,
                    }
                }
        except Exception as e:
            _logger.error(f'Sync error: {str(e)}')
            raise ValidationError(f'Sync error: {str(e)}')

    def get_latest_positions(self):
        """Get latest positions for all devices"""
        self.ensure_one()
        try:
            response = requests.get(
                f"{self.server_url}/api/positions",
                auth=(self.username, self.password),
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            _logger.error(f'Error getting positions: {str(e)}')
            return []


class TraccarLocationSync(models.Model):
    _name = 'ir.cron'
    _inherit = 'ir.cron'

    def _sync_traccar_locations(self):
        """Scheduled job to sync Traccar locations"""
        connections = self.env['traccar.connection'].search([('is_active', '=', True)])
        for connection in connections:
            positions = connection.get_latest_positions()
            location_obj = self.env['traccar.location']

            for pos in positions:
                location_obj.create({
                    'device_id': pos.get('deviceId'),
                    'connection_id': connection.id,
                    'latitude': pos.get('latitude'),
                    'longitude': pos.get('longitude'),
                    'speed': pos.get('speed'),
                    'course': pos.get('course'),
                    'accuracy': pos.get('accuracy'),
                    'altitude': pos.get('altitude'),
                    'timestamp': pos.get('serverTime'),
                })