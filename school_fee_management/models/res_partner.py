# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    """
    Extend res.partner to support student and parent relationships.
    This is the proper Odoo way - don't create separate student/parent models.
    """
    _inherit = 'res.partner'

    # Student-specific fields
    is_student = fields.Boolean(
        string='Is a Student',
        default=False,
        index=True  # INDEX: Fast filtering for student lists
    )

    student_id_number = fields.Char(
        string='Student ID',
        copy=False,
        index=True  # INDEX: Fast lookup by student ID
    )

    grade_level = fields.Selection([
        ('kindergarten', 'Kindergarten'),
        ('grade_1', 'Grade 1'),
        ('grade_2', 'Grade 2'),
        ('grade_3', 'Grade 3'),
        ('grade_4', 'Grade 4'),
        ('grade_5', 'Grade 5'),
        ('grade_6', 'Grade 6'),
        ('grade_7', 'Grade 7'),
        ('grade_8', 'Grade 8'),
        ('grade_9', 'Grade 9'),
        ('grade_10', 'Grade 10'),
        ('grade_11', 'Grade 11'),
        ('grade_12', 'Grade 12'),
    ], string='Grade Level', index=True)

    enrollment_date = fields.Date(string='Enrollment Date')

    # Parent relationship - use Odoo's built-in parent_id
    # parent_id already exists in res.partner for company hierarchies
    # We'll use it for student-parent relationships too

    # One2many relationships for easy navigation
    student_invoice_ids = fields.One2many(
        'school.student.invoice',
        'student_id',
        string='Student Invoices'
    )

    parent_invoice_ids = fields.One2many(
        'school.student.invoice',
        'parent_id',
        string='Children Invoices'
    )

    total_outstanding = fields.Monetary(
        string='Total Outstanding',
        compute='_compute_total_outstanding',
        currency_field='currency_id'
    )

    @api.depends('student_invoice_ids.amount_residual')
    def _compute_total_outstanding(self):
        """Calculate total outstanding balance for student"""
        for partner in self:
            if partner.is_student:
                partner.total_outstanding = sum(
                    partner.student_invoice_ids.filtered(
                        lambda inv: inv.state not in ['cancelled', 'paid']
                    ).mapped('amount_residual')
                )
            else:
                partner.total_outstanding = 0.0

    _sql_constraints = [
        ('student_id_unique',
         'UNIQUE(student_id_number)',
         'Student ID must be unique!'),
    ]