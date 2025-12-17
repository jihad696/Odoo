from odoo import models, fields

class Teacher(models.Model):
    _name = 'teacher'
    _inherit = 'person.base'
    _description = 'Teacher'
    _log_access = False

    hire_date = fields.Date()
    subject = fields.Char()
    course_ids = fields.One2many('course', 'teacher_id')
    student_ids = fields.Many2many('student')