# -*- coding: utf-8 -*-

from odoo import models, fields

class PosKitchenPrinter(models.Model):
    _name = "pos.kitchen.printer"
    _description = "POS Kitchen Printer"

    name = fields.Char(required=True)
    ip_address = fields.Char(string="Printer IP")
    port = fields.Integer(string="Port", default=9100)

    pos_config_ids = fields.Many2many(
        "pos.config",
        string="Point of Sale"
    )

    category_ids = fields.Many2many(
        "pos.category",
        string="Product Categories"
    )
