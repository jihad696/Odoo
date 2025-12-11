from odoo import models, fields


# SalesOrder won't be a new model in database this only override method and fields in sale.order
class SalesOrder(models.Model):
    _inherit = 'sale.order'

    property_id = fields.Many2one('property')

    def action_confirm(self):
        res = super(SalesOrder, self).action_confirm()
        print("inside action_confirm method")
        return res
