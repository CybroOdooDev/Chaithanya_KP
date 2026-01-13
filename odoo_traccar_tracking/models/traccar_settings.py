# -*- coding: utf-8 -*-

from odoo import models, fields

class TraccarSettings(models.Model):
    _name = "traccar.settings"
    _description = "Traccar Configuration"
    _rec_name = "name"

    name = fields.Char(default="Traccar Configuration", readonly=True)

    traccar_url = fields.Char(string="Traccar Server URL", required=True)
    traccar_username = fields.Char(string="Traccar Username", required=True)
    traccar_password = fields.Char(string="Traccar Password", required=True)
