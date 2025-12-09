from odoo import models, fields

class PersonBase (models.AbstractModel):
    _name = 'person.base'
    _log_access = False

    name = fields.Char()
    dob = fields.Date()
    email = fields.Char()
    active = fields.Boolean()







