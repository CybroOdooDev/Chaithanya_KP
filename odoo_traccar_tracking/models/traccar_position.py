# -*- coding: utf-8 -*-

from odoo import models, fields
import requests

class TraccarPosition(models.Model):
    _name = "traccar.position"
    _description = "Traccar Position"
    _order = "device_time desc"

    device_id = fields.Many2one("traccar.device", required=True)
    latitude = fields.Float()
    longitude = fields.Float()
    speed = fields.Float()
    device_time = fields.Datetime()

    def sync_positions(self):
        params = self.env["ir.config_parameter"].sudo()
        url = params.get_param("traccar.url")
        token = params.get_param("traccar.token")

        response = requests.get(

            f"{url}/api/positions",
            headers={"Authorization": f"Bearer {token}"}
        )

        for pos in response.json():
            device = self.env["traccar.device"].search(
                [("traccar_id", "=", pos["deviceId"])], limit=1
            )
            if device:
                self.create({
                    "device_id": device.id,
                    "latitude": pos["latitude"],
                    "longitude": pos["longitude"],
                    "speed": pos["speed"],
                    "device_time": pos["deviceTime"],
                })

