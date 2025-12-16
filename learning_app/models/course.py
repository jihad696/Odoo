from odoo import models, fields, api

class Course(models.Model):
    _name = 'course'
    _description = 'Course'

    name = fields.Char()
    code = fields.Char()
    description = fields.Char()
    student_ids = fields.Many2many('student')
    student_count = fields.Integer(compute='_compute_student_count', store=True)

    teacher_id = fields.Many2one('teacher')
    state = fields.Selection([
        ('draft','Draft'),
        ('pending','Pending'),
        ('confirm','Confirmed'),
    ], default='draft')

    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    def action_draft(self):
        self.state = 'draft'

    def action_pending(self):
        self.state = 'pending'

    def action_confirm(self):
        self.state = 'confirm'