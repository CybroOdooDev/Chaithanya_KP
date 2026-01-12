# -*- coding: utf-8 -*-

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    traccar_url = fields.Char("Traccar Server URL")
    traccar_api_token = fields.Char("Traccar API Token")

    def set_values(self):
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("traccar.url", self.traccar_url)
        params.set_param("traccar.token", self.traccar_api_token)

    def get_values(self):
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            traccar_url=params.get_param("traccar.url"),
            traccar_api_token=params.get_param("traccar.token"),
        )
        return res

