# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class TraccarWebhook(http.Controller):

    @http.route(
        '/traccar/webhook/position',
        type='json',
        auth='public',
        csrf=False,
        methods=['POST']
    )
    def traccar_position(self, **payload):
        """
        This method RECEIVES JSON from Traccar Server
        """
        device_id = payload.get('deviceId')
        latitude = payload.get('latitude')
        longitude = payload.get('longitude')
        speed = payload.get('speed')
        fix_time = payload.get('fixTime')
        print(latitude, longitude, speed, fix_time)
        print("Received position for device_id:", device_id)

        if not device_id:
            return {'status': 'error', 'message': 'No deviceId'}

        vehicle = request.env['fleet.vehicle'].sudo().search(
            [('traccar_device_id', '=', device_id)],
            limit=1
        )
        print("Received position for device_id:", device_id)

        if vehicle:
            vehicle.write({
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'last_gps_time': fix_time,
            })

        return {'status': 'success'}
