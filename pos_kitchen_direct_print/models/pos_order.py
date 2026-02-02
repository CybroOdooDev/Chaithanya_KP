# -*- coding: utf-8 -*-

from odoo import models, api

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def print_kitchen_order(self, order_data):
        """
        Entry point from POS JS
        """
        printers = self.env["pos.kitchen.printer"].search([
            ("pos_config_ids", "in", order_data.get("pos_config_id"))
        ])

        tickets = self._prepare_kitchen_tickets(order_data, printers)

        # Placeholder for real printing
        for printer, lines in tickets.items():
            self._send_to_printer(printer, lines)

        return True

    def _prepare_kitchen_tickets(self, order_data, printers):
        """
        Split order lines per printer based on category
        """
        tickets = {}

        for printer in printers:
            tickets[printer] = []

            for line in order_data.get("lines", []):
                product = self.env["product.product"].browse(line["product_id"])
                if product.pos_categ_id in printer.category_ids:
                    tickets[printer].append({
                        "qty": line["qty"],
                        "name": product.display_name,
                        "note": line.get("note"),
                    })

        return tickets

    def _send_to_printer(self, printer, lines):
        """
        Dummy printer logic (replace later with ESC/POS or socket)
        """
        if not lines:
            return

        message = "\n".join(
            f"{l['qty']} x {l['name']}" for l in lines
        )

        _logger = self.env["ir.logging"]
        _logger.create({
            "name": "Kitchen Print",
            "type": "server",
            "level": "INFO",
            "message": f"Printer: {printer.name}\n{message}",
            "path": __name__,
            "line": "0",
            "func": "_send_to_printer",
        })
