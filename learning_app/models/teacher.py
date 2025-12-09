
from odoo import models,fields




class Teacher(models.Model):
    _name = 'school.teacher'
    _log_access = False

    name = fields.Char()
    hire_date = fields.Date()
    subject = fields.Char()
    course_ids = fields.One2many('course','teacher_id')
    student_ids = fields.Many2many('student')
