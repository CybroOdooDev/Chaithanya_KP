# -*- coding: utf-8 -*-

from odoo import _,api, fields, models
from odoo.exceptions import UserError
import requests


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    traccar_device_id = fields.Integer("Traccar Device ID")
    latitude = fields.Float("Latitude", digits=(10, 7))
    longitude = fields.Float("Longitude", digits=(10, 7))
    speed = fields.Float("Speed")
    last_gps_time = fields.Datetime("Last GPS Time")

    def action_fetch_traccar_location(self):
        """
        Fetch latest position from Traccar server
        """
        ICP = self.env['ir.config_parameter'].sudo()

        url = ICP.get_param('traccar.url')
        username = ICP.get_param('traccar.username')
        password = ICP.get_param('traccar.password')

        if not all([url, username, password]):
            raise UserError("Configure Traccar credentials in Settings")

        response = requests.get(
            f"{url}/api/positions",
            auth=(username, password),
            timeout=10
        )

        response.raise_for_status()
        positions = response.json()

        for vehicle in self:
            for pos in positions:
                if pos.get('deviceId') == vehicle.traccar_device_id:
                    vehicle.write({
                        'latitude': pos.get('latitude'),
                        'longitude': pos.get('longitude'),
                        'speed': pos.get('speed'),
                        'last_gps_time': pos.get('fixTime'),
                    })
                    break