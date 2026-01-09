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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    """Inherits the stock picking to add the shipping details."""
    _inherit = 'stock.picking'

    label_id = fields.Many2one('easypost.label',
                               string="Easypost Label",
                               help="The Easypost shipping label")
    is_easypost = fields.Boolean(string='Easypost Shipping',
                                 help='True for Easypost shipping',
                                 compute='_compute_is_easypost')

    @api.depends('carrier_id')
    def _compute_is_easypost(self):
        """Method for computing is_easypost"""
        for rec in self:
            rec.is_easypost = True if (
                    rec.sale_id.carrier_id.delivery_type == 'easypost'
                    and self.env[
                        'easypost.label'].search_count([('picking_id', '=',
                                                         self.id)])) else False

    def cancel_shipment(self):
        """Method for canceling Easypost shipping"""
        res = super().cancel_shipment()
        if self.is_easypost:
            client = easypost.EasyPostClient(self.carrier_id.easypost_api_key)
            try:
                for rec in self.env['easypost.label'].sudo().search(
                        [('picking_id', '=', self.id)]):
                    shipment = client.shipment.retrieve(rec.shipping_ref)
                    if shipment:
                        refund = client.shipment.refund(rec.shipping_ref)
                        if refund:
                            self.sale_id.easypost_ref = False
                            self.carrier_tracking_ref = False
                            rec.unlink()
                        else:
                            raise ValidationError(
                                _("Failed to cancel the shipment. "
                                  "Please try again."))
            except easypost.errors.EasyPostError as e:
                raise ValidationError(_("EasyPost Error: %s") % str(e))
            except Exception as e:
                raise ValidationError(
                    _("An unexpected error occurred: %s") % str(e))
        return res

    def open_website_url(self):
        """Inherited for opening the tree view of easypost shipments"""
        if self.is_easypost:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Easypost Labels'),
                'view_mode': 'list',
                'res_model': 'easypost.label',
                'target': 'current',
                'domain': [('picking_id', '=', self.id)]
            }
        else:
            return super().open_website_url()

    def button_validate(self):
        """Override to add easypost shipment creation"""
        res = super().button_validate()
        if self.carrier_id and self.carrier_id.delivery_type == 'easypost':
            try:
                client = easypost.EasyPostClient(
                    self.carrier_id.easypost_api_key)
                shipment = client.shipment.retrieve(self.sale_id.easypost_ref)
                if self.move_line_ids.mapped('result_package_id'):
                    tracking = []
                    fee = 0.0
                    for package in self.move_line_ids.mapped(
                            'result_package_id'):
                        shipment = client.shipment.create(
                            to_address=shipment.to_address,
                            from_address=shipment.from_address,
                            parcel={
                                'predefined_package':
                                    package.package_type_id.name,
                                'weight': package.shipping_weight or 0.01,
                            }
                        )
                        if shipment.get("tracker"):
                            tracking.append(
                                shipment["tracker"].get("tracking_code"))
                        else:
                            rates = shipment.get("rates", [])
                            if rates:
                                lowest_rate = min(rates, key=lambda rate: float(
                                    rate["rate"]))
                                shipment = client.shipment.buy(
                                    id=shipment['id'], rate=lowest_rate)
                                tracking.append(shipment.get('tracking_code'))
                        if shipment.get("postage_label"):
                            label_url = shipment.get(
                                "postage_label")['label_url']
                            if label_url:
                                self.env['easypost.label'].sudo().create({
                                    'picking_id': self.id,
                                    'label': label_url,
                                    'tracking_ref': shipment.get('tracker')[
                                        'tracking_code'],
                                    'tracking_url': shipment.get('tracker')[
                                        'public_url'],
                                    'shipping_ref': shipment.get('id')
                                })
                        fee += sum(
                            float(fee["amount"]) for fee in shipment['fees'])
                    delivery = self.sale_id.order_line.filtered(
                        lambda x: x.is_delivery)
                    if delivery.price_unit != fee:
                        delivery.sudo().write({
                            'price_unit': fee
                        })
                    self.carrier_tracking_ref = ','.join(
                        [str(item) for item in tracking])
                else:
                    if shipment.get("tracker"):
                        self.carrier_tracking_ref = shipment["tracker"].get(
                            "tracking_code")
                    else:
                        rates = shipment.get("rates", [])
                        if rates:
                            lowest_rate = min(rates, key=lambda rate: float(
                                rate["rate"]))
                            shipment = client.shipment.buy(
                                id=self.sale_id.easypost_ref, rate=lowest_rate)
                            self.carrier_tracking_ref = shipment.get(
                                'tracking_code')
                    if shipment.get("postage_label"):
                        label_url = shipment.get(
                            "postage_label")['label_url']
                        if label_url and not self.env[
                            'easypost.label'].sudo().search(
                            [('picking_id', '=', self.id),
                             ('label', '=', label_url),
                             ('tracking_ref', '=',
                              shipment.get('tracker')[
                                  'tracking_code'])]):
                            self.env['easypost.label'].sudo().create({
                                'picking_id': self.id,
                                'label': label_url,
                                'tracking_ref': shipment.get('tracker')[
                                    'tracking_code'],
                                'tracking_url': shipment.get('tracker')[
                                    'public_url'],
                                'shipping_ref': shipment.get('id')
                            })
                    fee = sum(float(fee["amount"]) for fee in shipment['fees'])
                    delivery = self.sale_id.order_line.filtered(
                        lambda x: x.is_delivery)
                    if delivery.price_unit != fee:
                        delivery.sudo().write({
                            'price_unit': fee
                        })
            except easypost.errors.NotFoundError as e:
                error_message = _(
                    "The requested EasyPost shipment resource could not be "
                    "found. Please check the EasyPost reference.")
                raise ValidationError(error_message)
            except Exception as e:
                error_message = _("An unexpected error occurred: %s") % str(e)
                raise ValidationError(error_message)
        return res

    def send_to_shipper(self):
        """Override to avoid duplication issue"""
        if self.carrier_id.delivery_type != 'easypost':
            self.ensure_one()
            res = self.carrier_id.send_shipping(self)[0]
            if self.carrier_id.free_over and self.sale_id:
                amount_without_delivery = (
                    self.sale_id._compute_amount_total_without_delivery())
                if (self.carrier_id._compute_currency(self.sale_id,
                                                      amount_without_delivery,
                                                      'pricelist_to_company') >=
                        self.carrier_id.amount):
                    res['exact_price'] = 0.0
            self.carrier_price = res['exact_price'] * (
                    1.0 + (self.carrier_id.margin / 100.0))
            if res['tracking_number']:
                previous_pickings = self.env['stock.picking']
                accessed_moves = previous_moves = self.move_lines.move_orig_ids
                while previous_moves:
                    previous_pickings |= previous_moves.picking_id
                    previous_moves = previous_moves.move_orig_ids - accessed_moves
                    accessed_moves |= previous_moves
                without_tracking = previous_pickings.filtered(
                    lambda p: not p.carrier_tracking_ref)
                (self + without_tracking).carrier_tracking_ref = res[
                    'tracking_number']
                for p in previous_pickings - without_tracking:
                    p.carrier_tracking_ref += "," + res['tracking_number']
            order_currency = (self.sale_id.currency_id or
                              self.company_id.currency_id)
            msg = _(
                "Shipment sent to carrier %(carrier_name)s for "
                "shipping with tracking number"
                " %(ref)s<br/>Cost: %(price).2f %(currency)s",
                carrier_name=self.carrier_id.name,
                ref=self.carrier_tracking_ref,
                price=self.carrier_price,
                currency=order_currency.name
            )
            self.message_post(body=msg)
            self._add_delivery_cost_to_so()

    def _set_delivery_package_type(self, batch_pack=False):
        """ This method returns an action allowing to set the package type and
         the shipping weight
        on the stock.quant.package.
        """
        self.ensure_one()
        view_id = self.env.ref('stock_delivery.choose_delivery_package_view_form').id
        context = dict(
            self.env.context,
            current_package_carrier_type=self.carrier_id.delivery_type,
            default_picking_id=self.id,
            batch_pack=batch_pack,
        )
        if self.carrier_id.delivery_type == 'easypost':
            client = easypost.EasyPostClient(self.carrier_id.easypost_api_key)
            shipment = client.shipment.retrieve(self.sale_id.easypost_ref)
            rates = shipment.get("rates", [])
            lowest_rate = min(rates, key=lambda rate: float(rate["rate"]))
            context['easypost_carrier'] = lowest_rate.get("carrier")
        if context['current_package_carrier_type'] in ['fixed', 'base_on_rule']:
            context['current_package_carrier_type'] = 'none'
        return {
            'name': _('Package Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.package',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }
