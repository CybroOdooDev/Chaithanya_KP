import requests
from odoo import models, fields

class TraccarDevice(models.Model):
    _name = "traccar.device"
    _description = "Traccar Device"

    name = fields.Char(required=True)
    traccar_id = fields.Integer(string="Traccar ID")
    unique_id = fields.Char(string="Unique Identifier")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Fleet Vehicle")


    def action_sync_devices(self):
        param = self.env["ir.config_parameter"].sudo()
        url = param.get_param("traccar.url")
        user = param.get_param("traccar.username")
        pwd = param.get_param("traccar.password")

        response = requests.get(
            f"{url}/api/devices",
            auth=(user, pwd),
            timeout=15
        )
        response.raise_for_status()

        for device in response.json():
            self.search([("traccar_id", "=", device["id"])], limit=1).unlink()
            self.create({
                "name": device["name"],
                "traccar_id": device["id"],
                "unique_id": device["uniqueId"],
            })
