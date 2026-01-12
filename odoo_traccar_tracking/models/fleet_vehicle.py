# -*- coding: utf-8 -*- 

from odoo import models, fields

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    traccar_device_id = fields.Many2one("traccar.device")
