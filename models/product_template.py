from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tipo = fields.Char(string="Tipo")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    tipo = fields.Char(string="Tipo")
