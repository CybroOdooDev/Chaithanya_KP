from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_maps_api_key = fields.Char(
        string='Google Maps API Key',
        help='API key from Google Cloud Console with Maps JavaScript API enabled'
    )
    google_geocoding_api_key = fields.Char(
        string='Google Geocoding API Key',
        help='API key for reverse geocoding (can be same as above)'
    )
    location_update_interval = fields.Integer(
        string='Location Update Interval (seconds)',
        default=30,
        help='Frequency of GPS location updates'
    )
    track_vehicle_speed = fields.Boolean(
        string='Track Vehicle Speed',
        default=True,
        help='Enable speed monitoring and alerts'
    )
    speed_limit_alert = fields.Float(
        string='Speed Limit Alert Threshold (km/h)',
        default=80.0,
        help='Alert when vehicle exceeds this speed'
    )
    enable_geofencing = fields.Boolean(
        string='Enable Geofencing',
        default=True,
        help='Monitor vehicle entry/exit from defined areas'
    )
    enable_trip_tracking = fields.Boolean(
        string='Enable Trip Tracking',
        default=True,
        help='Track vehicle trips and duration'
    )
    idle_time_threshold = fields.Integer(
        string='Idle Time Threshold (minutes)',
        default=5,
        help='Minutes before vehicle is considered idle'
    )
    maps_zoom_level = fields.Integer(
        string='Maps Default Zoom Level',
        default=15,
        help='Default zoom level for map displays'
    )
    show_location_history = fields.Boolean(
        string='Show Location History on Map',
        default=True,
        help='Display vehicle route history'
    )
    api_connection_status = fields.Char(
        string='API Connection Status',
        readonly=True,
        compute='_compute_api_status'
    )

    @api.depends('google_maps_api_key')
    def _compute_api_status(self):
        """Verify Google Maps API key validity"""
        for record in self:
            if not record.google_maps_api_key:
                record.api_connection_status = "Not Configured"
                continue

            try:
                from .google_maps_api import GoogleMapsAPI
                api = GoogleMapsAPI(record.google_maps_api_key)
                if api.verify_api_key():
                    record.api_connection_status = "✓ Valid & Connected"
                else:
                    record.api_connection_status = "✗ Invalid API Key"
            except Exception as e:
                record.api_connection_status = f"✗ Error: {str(e)[:50]}"

    def set_values(self):
        """Save configuration"""
        super().set_values()

        if self.google_maps_api_key and len(self.google_maps_api_key) < 20:
            raise ValidationError("Invalid Google Maps API key format")

        param = self.env['ir.config_parameter'].sudo()
        param.set_param('fleet_geolocation.google_maps_api_key', self.google_maps_api_key or '')
        param.set_param('fleet_geolocation.google_geocoding_api_key', self.google_geocoding_api_key or '')
        param.set_param('fleet_geolocation.location_update_interval', self.location_update_interval)
        param.set_param('fleet_geolocation.track_vehicle_speed', self.track_vehicle_speed)
        param.set_param('fleet_geolocation.speed_limit_alert', self.speed_limit_alert)
        param.set_param('fleet_geolocation.enable_geofencing', self.enable_geofencing)
        param.set_param('fleet_geolocation.enable_trip_tracking', self.enable_trip_tracking)
        param.set_param('fleet_geolocation.idle_time_threshold', self.idle_time_threshold)
        param.set_param('fleet_geolocation.maps_zoom_level', self.maps_zoom_level)
        param.set_param('fleet_geolocation.show_location_history', self.show_location_history)

    def get_values(self):
        """Retrieve configuration"""
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo()

        res.update({
            'google_maps_api_key': param.get_param('fleet_geolocation.google_maps_api_key', ''),
            'google_geocoding_api_key': param.get_param('fleet_geolocation.google_geocoding_api_key', ''),
            'location_update_interval': int(param.get_param('fleet_geolocation.location_update_interval', 30)),
            'track_vehicle_speed': param.get_param('fleet_geolocation.track_vehicle_speed', True),
            'speed_limit_alert': float(param.get_param('fleet_geolocation.speed_limit_alert', 80.0)),
            'enable_geofencing': param.get_param('fleet_geolocation.enable_geofencing', True),
            'enable_trip_tracking': param.get_param('fleet_geolocation.enable_trip_tracking', True),
            'idle_time_threshold': int(param.get_param('fleet_geolocation.idle_time_threshold', 5)),
            'maps_zoom_level': int(param.get_param('fleet_geolocation.maps_zoom_level', 15)),
            'show_location_history': param.get_param('fleet_geolocation.show_location_history', True),
        })
        return res

    def action_test_api_connection(self):
        """Test Google Maps API connection"""
        self.ensure_one()

        if not self.google_maps_api_key:
            raise ValidationError("Please enter Google Maps API Key")

        try:
            from .google_maps_api import GoogleMapsAPI
            api = GoogleMapsAPI(self.google_maps_api_key)

            if api.verify_api_key():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Google Maps API connection verified successfully!',
                        'type': 'success',
                    }
                }
            else:
                raise ValidationError("Invalid Google Maps API key")
        except Exception as e:
            raise ValidationError(f"API Connection Error: {str(e)}")
