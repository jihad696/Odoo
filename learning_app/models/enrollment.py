from odoo import models,fields



class Enrollment(models.Model):
    _name = 'school.enrollment'

    enrollment_date = fields.Date()

