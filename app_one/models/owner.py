from odoo import models,fields

class Owner(models.Model):

    _name = 'owner'

    name = fields.Char(required=True)
    phone_number = fields.Char()
    address = fields.Char()
    description=fields.Char()
    property_ids = fields.One2many('property','owner_id')


