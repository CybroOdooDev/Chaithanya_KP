# -- coding: utf-8 --
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Subina P (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
import easypost
from odoo import fields, models, _
from odoo.exceptions import ValidationError


class DeliveryCarrier(models.Model):
    """Inherited delivery carrier for adding Easypost fields and functions"""
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[
            ('easypost', 'Easypost'),
        ], ondelete={'easypost': 'cascade'}, help='Type of delivery')
    easypost_api_key = fields.Char(string='API Key',
                                   help="API Key used to connect with partner")

    def rate_shipment(self, order):
        """Override rate_shipment method for calculating the rate for
        shipment"""
        self.ensure_one()
        if self.delivery_type == 'easypost':
            client = easypost.EasyPostClient(self.easypost_api_key)
            shipment = client.shipment.create(
                to_address={
                    'name': order.partner_id.name,
                    'street1': order.partner_id.street,
                    'street2': order.partner_id.street2,
                    'city': order.partner_id.city,
                    'state': order.partner_id.state_id.name,
                    'zip': order.partner_id.zip,
                    'country': order.partner_id.country_id.name,
                    'phone': order.partner_id.phone
                },
                from_address={
                    'name': order.warehouse_id.partner_id.name,
                    'street1': order.warehouse_id.partner_id.street,
                    'street2': order.warehouse_id.partner_id.street2,
                    'city': order.warehouse_id.partner_id.city,
                    'state': order.warehouse_id.partner_id.state_id.name,
                    'zip': order.warehouse_id.partner_id.zip,
                    'country': order.warehouse_id.partner_id.country_id.name,
                    'phone': order.warehouse_id.partner_id.phone
                },
                parcel={
                    "weight": order._get_estimated_weight(),
                }
            )
            if not shipment.rates:
                raise ValidationError(
                    "There are no carriers available for the specified "
                    "address.")
            rates = shipment["rates"]
            lowest_rate = min(rates, key=lambda rate: float(rate["rate"]))
            if order.currency_id.name == lowest_rate['currency']:
                rate = float(lowest_rate['rate'])
            else:
                currency = self.env['res.currency'].search(
                    [('name', '=', lowest_rate['currency'])], limit=1)
                rate = currency._convert(float(lowest_rate['rate']),
                                         order.currency_id, self.env.company,
                                         fields.Date.today())
            order.sudo().write({
                'easypost_ref': shipment['id']})
            res = {
                'success': True,
                'error_message': False,
                'warning_message': False,
                'price': rate,
                'carrier_price': rate,
            }
            carrier_metadata = client.carrier_metadata.retrieve(
                carriers=[lowest_rate.get("carrier")]
            )
            for rec in carrier_metadata[0]['predefined_packages']:
                if rec['dimensions']:
                    length, width, height = self.parse_dimensions(
                        rec['dimensions'][0])
                else:
                    length, width, height = None, None, None
                if not self.env['stock.package.type'].sudo().search(
                        [('package_carrier_type', '=', 'easypost'),
                         ('carrier', '=', lowest_rate.get("carrier")),
                         ('name', '=', rec.name)]):
                    self.env['stock.package.type'].sudo().create({
                        'package_carrier_type': 'easypost',
                        'name': rec.name,
                        'height': height,
                        'width': width,
                        'packaging_length': length,
                        'max_weight': rec['max_weight'],
                        'carrier': lowest_rate.get("carrier")
                    })
            return res
        return super().rate_shipment(order)

    def parse_dimensions(self, dimensions_str):
        """Method for returning the dimensions from dimensions_str"""
        dimensions = dimensions_str.split(" x ")
        parsed_dimensions = []
        for dim in dimensions:
            if "in" in dim:
                parsed_dimensions.append(float(dim.replace("in", "")))
            else:
                parsed_dimensions.append(0.0)
        # Ensure the length of parsed_dimensions is 3
        while len(parsed_dimensions) < 3:
            parsed_dimensions.append(0.0)
        return tuple(parsed_dimensions)
