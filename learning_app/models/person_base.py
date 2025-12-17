# models/person_base.py
from odoo import models, fields, api


class PersonBase(models.AbstractModel):
    _name = 'person.base'
    _description = 'Person Base Model'

    name = fields.Char(string='Name', required=True)
    dob = fields.Date(string='Date of Birth')
    email = fields.Char(string='Email')
    phone_number = fields.Char(string='Phone Number')
    active = fields.Boolean(string='Active', default=True)
    image = fields.Binary(string='Photo', attachment=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')
    address = fields.Char(string='Address')

    _sql_constraints = [
        ('unique_phone', 'UNIQUE(phone_number)', 'Phone number already exists!')
    ]

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("Please enter a valid email address")