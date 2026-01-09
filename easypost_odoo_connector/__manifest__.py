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
{
    'name': "Easypost Odoo Connector",
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': """Integrates Your Easypost Shipping from Odoo.""",
    'description': """By integrating EasyPost with Odoo, you can speed up your 
     shipping procedures and decrease the time needed for shipment preparation. 
     With the help of EasyPost, you can easily integrate with all the major
     carriers.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['delivery', 'stock_delivery', 'website_sale','sale_management','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/easypost_label_views.xml',
        'views/delivery_carrier_views.xml',
        # 'views/choose_delivery_package_views.xml',
        'views/choose_delivery_carrier_views.xml'
    ],
    'demo': [
        'demo/product_template_demo.xml'
    ],
    'external_dependencies': {
        'python': ['easypost']
    },
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
