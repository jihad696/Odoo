# enrollment.py (optional - remove or keep as placeholder)
from odoo import models, fields


class Enrollment(models.Model):
    _name = 'enrollment'
    _description = 'Enrollment'

    enrollment_date = fields.Date()