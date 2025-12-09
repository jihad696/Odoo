from odoo import models
from odoo import fields,api
from odoo.fields import Many2one
from odoo.tools import Query


class Course(models.Model):
    _name = 'course'


    name = fields.Char()
    code = fields.Char()
    description = fields.Char()
    student_ids = fields.Many2many('student')
    student_count = fields.Integer(compute='_compute_student_count')
    teacher_id = fields.Many2one('school.teacher')




    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)




    @api.model_create_multi
    def create(self,vals):
        res = super(Course,self).create(vals)
        print('Hello there from create course')
        return res


    @api.model
    def _search(self, domain, offset=0, limit=None, order=None) -> Query:
        res = super(Course,self)._search(domain, offset=0, limit=None, order=None)
        print(' read from search')
        return res


    def unlink(self):
        res = super(Course,self).unlink()
        print('from unlink method')
        return res


    def write(self,vals):
        res = super(Course,self).write(vals)
        print('this is from write')
        return res
