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
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DeliveryPartner(models.Model):
    """Class for storing the details of delivery partner"""
    _name = 'delivery.partner'
    _description = 'Delivery Partner'

    name = fields.Char(string="Name", help="The type of shipping")
    api_key = fields.Char(string='API Key',
                          help="API Key used to connect with partner")

    @api.onchange('api_key')
    def onchange_api_key(self):
        """Function cor creating easypost carrier, package and service"""
        if self.api_key:
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            carriers = requests.request("GET",
                                        "https://api.easypost.com/"
                                        "v2/carrier_accounts/",
                                        headers=headers)
            if type(carriers.json()) == dict:
                raise ValidationError(_(
                    carriers.json()['error']['message']))
            for carrier in carriers.json():
                if (carrier['id'] not in self.env['easypost.carrier'].search(
                        []).mapped('carrier')):
                    carrier_id = self.env['easypost.carrier'].create({
                        'name': carrier['readable'],
                        'carrier': carrier['id']
                    })
                    metadata = requests.request("GET",
                                                "https://api.easypost.com/"
                                                "beta/metadata/",
                                                headers=headers)
                    if type(carriers.json()) == dict:
                        raise ValidationError(
                            carriers.json()['error']['message'])
                    services = next((rec['service_levels'] for rec in
                                     metadata.json()['carriers'] if
                                     rec.get('human_readable') == carrier[
                                         'readable']))
                    packages = next((rec['predefined_packages'] for rec in
                                     metadata.json()['carriers'] if
                                     rec.get('human_readable') == carrier[
                                         'readable']))
                    for service in services:
                        if (service['name'] not in self.env[
                            'easypost.service'].search(
                            [('carrier_id', '=', carrier_id.id),
                             ('name', '=', service['name'])]).
                                mapped('name')):
                            self.env['easypost.service'].create({
                                'name': service['name'],
                                'carrier_id': carrier_id.id
                            })
                    for package in packages:
                        if package['name'] not in self.env[
                            'easypost.package'].search(
                            [('carrier_id', '=', carrier_id.id),
                             ('name', '=', package['name'])]).mapped('name'):
                            self.env['easypost.package'].create({
                                'name': package['name'],
                                'carrier_id': carrier_id.id
                            })
