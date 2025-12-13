from odoo import models,fields,api
from odoo.exceptions import ValidationError


class Student(models.Model):
    _name = 'student'

    # _inherit = 'base.user'

    name = fields.Char()
    age =fields.Integer()
    hobby= fields.Char()
    phone_number = fields.Char()
    grade = fields.Selection(

        [
            ('grade_one','1'),
            ('grade_two','2'),
            ('grade_three','3')
        ]
    )

    course_ids = fields.Many2many('course')
    course_code = fields.Char()


    _sql_constraints = [
        ('unique_phone', 'UNIQUE(phone_number)', 'Phone number already exists!')
    ]






    @api.constrains('age')
    def _check_age(self):
        for rec in self:
            if rec.age is None:
                raise ValidationError("Age cannot be empty")
            if rec.age < 0:
                raise ValidationError("Age must be a positive number!")
            if rec.age == 0:
                raise ValidationError("Age cannot be zero!")
            if rec.age > 18:
                raise ValidationError("Age cannot be greater than 18!")
