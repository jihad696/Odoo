# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FeeType(models.Model):
    """
    Master data for different types of fees (tuition, books, etc.)
    This acts as a catalog that can be reused across different grade levels.
    """
    _name = 'school.fee.type'
    _description = 'Fee Type'
    _order = 'sequence, name'

    name = fields.Char(string='Fee Type', required=True, translate=True)
    code = fields.Char(string='Code', required=True, size=10)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    # SQL constraint for unique code - ensures data integrity at database level
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Fee type code must be unique!'),
    ]


class FeeStructure(models.Model):
    """
    Defines the fee structure for each grade level.
    Links fee types with amounts and recurrence rules.

    OPTIMIZATION NOTES:
    - grade_level indexed for fast filtering by grade
    - active field for soft deletes (keeps historical data)
    - _sql_constraints prevent duplicate fee types per grade
    """
    _name = 'school.fee.structure'
    _description = 'School Fee Structure'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Audit trail capability
    _order = 'grade_level, fee_type_id'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    fee_type_id = fields.Many2one(
        'school.fee.type',
        string='Fee Type',
        required=True,
        ondelete='restrict',  # Prevent deletion if used
        index=True  # INDEX: Fast lookup when generating invoices
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
    ], string='Grade Level', required=True, index=True, tracking=True)

    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    recurrence = fields.Selection([
        ('one_time', 'One Time'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semester', 'Semester'),
        ('annual', 'Annual'),
    ], string='Recurrence', required=True, default='semester', tracking=True)

    # Discount configuration
    discount_type = fields.Selection([
        ('none', 'No Discount'),
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ], string='Discount Type', default='none', tracking=True)

    discount_value = fields.Float(
        string='Discount Value',
        help='Percentage (0-100) or Fixed Amount depending on discount type'
    )

    active = fields.Boolean(string='Active', default=True)
    academic_year = fields.Char(string='Academic Year', default='2024-2025')

    # Computed field for display
    @api.depends('fee_type_id', 'grade_level', 'academic_year')
    def _compute_name(self):
        """Generate descriptive name for the fee structure"""
        for record in self:
            if record.fee_type_id and record.grade_level:
                grade_name = dict(self._fields['grade_level'].selection).get(record.grade_level)
                record.name = f"{record.fee_type_id.name} - {grade_name} ({record.academic_year})"
            else:
                record.name = 'New Fee Structure'

    @api.constrains('discount_value', 'discount_type')
    def _check_discount_value(self):
        """Validate discount values based on discount type"""
        for record in self:
            if record.discount_type == 'percentage':
                if record.discount_value < 0 or record.discount_value > 100:
                    raise ValidationError(_('Percentage discount must be between 0 and 100.'))
            elif record.discount_type == 'fixed':
                if record.discount_value < 0:
                    raise ValidationError(_('Fixed discount cannot be negative.'))
                if record.discount_value > record.amount:
                    raise ValidationError(_('Fixed discount cannot exceed the fee amount.'))

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        """Reset discount value when discount type changes"""
        if self.discount_type == 'none':
            self.discount_value = 0.0

    def calculate_final_amount(self):
        """
        Calculate the final amount after applying discounts.
        Used by invoice generation logic.
        """
        self.ensure_one()
        final_amount = self.amount

        if self.discount_type == 'percentage':
            final_amount = self.amount * (1 - self.discount_value / 100)
        elif self.discount_type == 'fixed':
            final_amount = self.amount - self.discount_value

        return max(final_amount, 0)  # Never return negative

    # SQL constraints for data integrity
    _sql_constraints = [
        ('fee_grade_unique',
         'UNIQUE(fee_type_id, grade_level, academic_year)',
         'This fee type already exists for this grade level and academic year!'),
        ('amount_positive',
         'CHECK(amount >= 0)',
         'Fee amount must be positive!'),
    ]