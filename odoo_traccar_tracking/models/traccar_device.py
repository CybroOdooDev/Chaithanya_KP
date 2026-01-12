# *- coding: utf-8 -*-

from odoo import models, fields
import requests

class TraccarDevice(models.Model):
    _name = "traccar.device"
    _description = "Traccar Device"

    name = fields.Char(required=True)
    traccar_id = fields.Integer(required=True, index=True)
    unique_id = fields.Char()
    vehicle_id = fields.Many2one("fleet.vehicle")

    def action_sync_devices(self):
        params = self.env["ir.config_parameter"].sudo()
        url = params.get_param("traccar.url")
        token = params.get_param("traccar.token")

        response = requests.get(
            f"{url}/api/devices",
            headers={"Authorization": f"Bearer {token}"}
        )

        for dev in response.json():
            device = self.search([("traccar_id", "=", dev["id"])], limit=1)
            values = {
                "name": dev["name"],
                "traccar_id": dev["id"],
                "unique_id": dev.get("uniqueId"),
            }
            if device:
                device.write(values)
            else:
                self.create(values)
