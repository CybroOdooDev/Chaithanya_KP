from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    traccar_url = fields.Char(
        string="Traccar Server URL",
        help="e.g., http://192.168.1.100:8082 or https://traccar.example.com"
    )
    traccar_username = fields.Char(
        string="Traccar Username",
        help="Username for Traccar API authentication"
    )
    traccar_password = fields.Char(
        string="Traccar Password",
        help="Password for Traccar API authentication"
    )
    traccar_connection_status = fields.Char(
        string="Connection Status",
        readonly=True,
        compute="_compute_connection_status"
    )
    traccar_auto_sync = fields.Boolean(
        string="Enable Auto Sync",
        default=False,
        help="Automatically sync locations every 5 minutes"
    )

    @api.depends('traccar_url', 'traccar_username', 'traccar_password')
    def _compute_connection_status(self):
        """Check if Traccar server is accessible"""
        for record in self:
            if not record.traccar_url:
                record.traccar_connection_status = "Not Configured"
                continue

            try:
                from .traccar_api import TraccarAPI
                api = TraccarAPI(
                    record.traccar_url,
                    record.traccar_username,
                    record.traccar_password
                )
                if api.test_connection():
                    record.traccar_connection_status = "✓ Connected"
                else:
                    record.traccar_connection_status = "✗ Connection Failed"
            except Exception as e:
                record.traccar_connection_status = f"✗ Error: {str(e)}"

    def set_values(self):
        """Save Traccar configuration"""
        super().set_values()

        # Validate URL
        if self.traccar_url and not self.traccar_url.startswith(('http://', 'https://')):
            raise ValidationError("Traccar URL must start with http:// or https://")

        param = self.env["ir.config_parameter"].sudo()
        param.set_param("traccar.url", self.traccar_url or "")
        param.set_param("traccar.username", self.traccar_username or "")
        param.set_param("traccar.password", self.traccar_password or "")
        param.set_param("traccar.auto_sync", self.traccar_auto_sync)

    def get_values(self):
        """Retrieve Traccar configuration"""
        res = super().get_values()
        param = self.env["ir.config_parameter"].sudo()

        res.update({
            'traccar_url': param.get_param("traccar.url", ""),
            'traccar_username': param.get_param("traccar.username", ""),
            'traccar_password': param.get_param("traccar.password", ""),
            'traccar_auto_sync': param.get_param("traccar.auto_sync", False),
        })
        return res

    def action_test_connection(self):
        """Test Traccar server connection"""
        self.ensure_one()

        if not self.traccar_url or not self.traccar_username or not self.traccar_password:
            raise ValidationError("Please fill in Traccar URL, Username, and Password")

        try:
            from .traccar_api import TraccarAPI
            api = TraccarAPI(
                self.traccar_url,
                self.traccar_username,
                self.traccar_password
            )

            if api.test_connection():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': 'Connected to Traccar server successfully!',
                        'type': 'success',
                    }
                }
            else:
                raise ValidationError("Failed to connect to Traccar server")
        except Exception as e:
            raise ValidationError(f"Connection Error: {str(e)}")

