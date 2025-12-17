from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = 'student'
    _inherit = 'person.base'

    age = fields.Integer()
    hobby = fields.Char()
    grade = fields.Selection([
        ('grade_one','1'),
        ('grade_two','2'),
        ('grade_three','3')
    ])

    course_ids = fields.Many2many('course')
    course_code = fields.Char(compute='_compute_course_code', store=True)
    user_id = fields.Many2one('res.users', string='User')

    @api.depends('course_ids')
    def _compute_course_code(self):
        for student in self:
            if student.course_ids:
                student.course_code = ', '.join(student.course_ids.mapped('name'))
            else:
                student.course_code = ''

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