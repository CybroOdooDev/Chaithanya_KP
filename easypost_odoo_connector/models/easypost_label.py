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
from odoo import fields, models, _
from odoo.exceptions import UserError


class EasypostLabel(models.Model):
    """Class for storing the details of delivery partner"""
    _name = 'easypost.label'
    _description = 'Easypost Label'

    # picking_id = fields.Many2one(string="Picking",
    #                              help="Picking correspinding to the label")
    picking_id = fields.Many2one('stock.picking',string="Picking",
                                 help="Picking corresponding to the label",)
    label = fields.Char(string='Label',
                        help="Easypost label")
    tracking_url = fields.Char(string='Tracking Url',
                               help="Url for tracking the shipment")
    tracking_ref = fields.Char(string="Tracking Id",
                               help='Reference for tracking easypost shipment')
    shipping_ref = fields.Char(string="Shipping",
                               help="Id of Easypost shipping")

    def action_download_label(self):
        """Method for redirecting the Easypost label"""
        self.ensure_one()
        if not self.label:
            raise UserError(_('No label to download.'))
        return {
            'type': 'ir.actions.act_url',
            'url': self.label,
            'target': 'self',
        }

    def action_track_shipment(self):
        """Method for redirecting the Easypost tracking"""
        self.ensure_one()
        if not self.tracking_url:
            raise UserError(_('No tracking url.'))
        return {
            'type': 'ir.actions.act_url',
            'url': self.tracking_url,
            'target': 'self',
        }
