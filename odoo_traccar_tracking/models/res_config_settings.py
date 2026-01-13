from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    traccar_url = fields.Char(string="Traccar Server URL")
    traccar_username = fields.Char(string="Traccar Username")
    traccar_password = fields.Char(string="Traccar Password")

    def set_values(self):
        super().set_values()
        param = self.env["ir.config_parameter"].sudo()
        param.set_param("traccar.url", self.traccar_url)
        param.set_param("traccar.username", self.traccar_username)
        param.set_param("traccar.password", self.traccar_password)

    def get_values(self):
        res = super().get_values()
        param = self.env["ir.config_parameter"].sudo()
        res.update(
            traccar_url=param.get_param("traccar.url"),
            traccar_username=param.get_param("traccar.username"),
            traccar_password=param.get_param("traccar.password"),
        )
        return res
