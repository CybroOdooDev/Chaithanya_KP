# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class TraccarWebhook(http.Controller):

    @http.route("/traccar/webhook", type="json", auth="public", csrf=False)
    def webhook(self, **payload):
        event = payload.get("event")
        if event:
            request.env["traccar.event"].sudo().create({
                "event_type": event.get("type"),
                "device_id": event.get("deviceId"),
                "event_time": event.get("serverTime"),
            })
        return {"status": "ok"}
