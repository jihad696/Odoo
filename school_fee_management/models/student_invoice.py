# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class StudentInvoice(models.Model):
    """
    Bridge model connecting students to their invoices.
    This model tracks the relationship and adds student-specific metadata.

    PERFORMANCE OPTIMIZATION:
    - student_id indexed: Fast filtering in parent portal
    - invoice_id indexed: Fast joins with account.move
    - state indexed: Fast filtering by payment status
    - invoice_date indexed: Fast date range queries for reports

    WHY NOT JUST USE account.move DIRECTLY?
    - Separation of concerns: School logic vs accounting logic
    - Additional fields specific to school operations
    - Easier to add school-specific workflows
    - Better performance with targeted indexes
    """
    _name = 'school.student.invoice'
    _description = 'Student Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'invoice_date desc, id desc'
    _rec_name = 'display_name'

    # Core relationships - all indexed for performance
    student_id = fields.Many2one(
        'res.partner',
        string='Student',
        required=True,
        ondelete='cascade',
        domain="[('is_student', '=', True)]",
        index=True,  # INDEX: Critical for parent portal filtering
        tracking=True
    )

    parent_id = fields.Many2one(
        'res.partner',
        string='Parent/Guardian',
        compute='_compute_parent_id',
        store=True,
        index=True  # INDEX: Fast filtering in parent portal record rules
    )

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        required=True,
        ondelete='cascade',
        domain="[('move_type', '=', 'out_invoice')]",
        index=True,  # INDEX: Fast joins with accounting module
        tracking=True
    )

    # Denormalized fields for performance
    # WHY DENORMALIZE? Avoids joins when displaying lists
    invoice_date = fields.Date(
        string='Invoice Date',
        related='invoice_id.invoice_date',
        store=True,
        index=True,  # INDEX: Fast date range filtering in reports
        readonly=True
    )

    due_date = fields.Date(
        string='Due Date',
        related='invoice_id.invoice_date_due',
        store=True,
        readonly=True
    )

    amount_total = fields.Monetary(
        string='Total Amount',
        related='invoice_id.amount_total',
        store=True,
        readonly=True
    )

    amount_residual = fields.Monetary(
        string='Amount Due',
        related='invoice_id.amount_residual',
        store=True,
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='invoice_id.currency_id',
        store=True,
        readonly=True
    )

    # State management with proper workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True,
        index=True,  # INDEX: Fast filtering by status
        tracking=True,
        copy=False)

    # School-specific fields
    grade_level = fields.Selection(
        related='student_id.grade_level',
        store=True,
        string='Grade Level'
    )

    semester = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Semester', tracking=True)

    academic_year = fields.Char(string='Academic Year', default='2024-2025')

    # Computed fields with proper dependencies
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        search='_search_is_overdue'  # Makes field searchable
    )

    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_is_overdue'
    )

    payment_percentage = fields.Float(
        string='Payment %',
        compute='_compute_payment_percentage',
        store=True
    )

    # Related fields for easy access
    invoice_state = fields.Selection(
        related='invoice_id.state',
        string='Invoice State',
        store=True
    )

    @api.depends('student_id', 'invoice_id')
    def _compute_display_name(self):
        """Generate user-friendly display name"""
        for record in self:
            if record.student_id and record.invoice_id:
                record.display_name = f"{record.student_id.name} - {record.invoice_id.name}"
            else:
                record.display_name = 'New Student Invoice'

    @api.depends('student_id.parent_id')
    def _compute_parent_id(self):
        """
        Link to parent for record rule filtering.
        CRITICAL for security: Ensures parents only see their children's invoices.
        """
        for record in self:
            record.parent_id = record.student_id.parent_id

    @api.depends('due_date', 'state', 'amount_residual')
    def _compute_is_overdue(self):
        """
        Determine if invoice is overdue.
        Used in kanban views and reports.
        """
        today = fields.Date.today()
        for record in self:
            if record.due_date and record.amount_residual > 0 and record.state not in ['paid', 'cancelled']:
                if record.due_date < today:
                    record.is_overdue = True
                    record.days_overdue = (today - record.due_date).days
                else:
                    record.is_overdue = False
                    record.days_overdue = 0
            else:
                record.is_overdue = False
                record.days_overdue = 0

    def _search_is_overdue(self, operator, value):
        """
        Make is_overdue searchable in domain filters.
        Example: [('is_overdue', '=', True)]
        """
        today = fields.Date.today()
        if (operator == '=' and value) or (operator == '!=' and not value):
            # Search for overdue invoices
            return [
                ('due_date', '<', today),
                ('amount_residual', '>', 0),
                ('state', 'not in', ['paid', 'cancelled'])
            ]
        else:
            # Search for not overdue invoices
            return ['|', '|', '|',
                    ('due_date', '>=', today),
                    ('amount_residual', '=', 0),
                    ('state', '=', 'paid'),
                    ('state', '=', 'cancelled')
                    ]

    @api.depends('amount_total', 'amount_residual')
    def _compute_payment_percentage(self):
        """Calculate what percentage has been paid"""
        for record in self:
            if record.amount_total > 0:
                paid_amount = record.amount_total - record.amount_residual
                record.payment_percentage = (paid_amount / record.amount_total) * 100
            else:
                record.payment_percentage = 0.0

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        """Auto-update state based on invoice state"""
        if self.invoice_id:
            if self.invoice_id.state == 'draft':
                self.state = 'draft'
            elif self.invoice_id.state == 'posted':
                if self.invoice_id.payment_state == 'paid':
                    self.state = 'paid'
                elif self.invoice_id.payment_state == 'partial':
                    self.state = 'partial'

    def action_send_invoice(self):
        """
        Send invoice to parent via email.
        Updates state to 'sent'.
        """
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft invoices can be sent.'))

        # Post the accounting invoice if still in draft
        if self.invoice_id.state == 'draft':
            self.invoice_id.action_post()

        # Send email using Odoo's invoice send wizard
        self.state = 'sent'
        self.message_post(
            body=_('Invoice sent to parent: %s') % self.parent_id.name,
            subject=_('Invoice Sent')
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.send',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'account.move',
                'active_id': self.invoice_id.id,
            }
        }

    def action_mark_paid(self):
        """Mark invoice as paid (for manual reconciliation)"""
        self.ensure_one()
        if self.state == 'paid':
            raise UserError(_('Invoice is already marked as paid.'))

        self.write({'state': 'paid'})
        self.message_post(
            body=_('Invoice manually marked as paid by %s') % self.env.user.name,
            subject=_('Invoice Paid')
        )

    def action_cancel(self):
        """Cancel invoice with audit trail"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_('Cannot cancel a paid invoice.'))

            record.state = 'cancelled'
            record.message_post(
                body=_('Invoice cancelled by %s') % self.env.user.name,
                subject=_('Invoice Cancelled')
            )

    def action_reset_to_draft(self):
        """Reset to draft for corrections"""
        for record in self:
            if record.state == 'paid':
                raise UserError(_('Cannot reset a paid invoice to draft.'))

            record.state = 'draft'
            if record.invoice_id.state == 'posted':
                record.invoice_id.button_draft()

    def action_view_invoice(self):
        """Open the related accounting invoice"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    @api.model
    def auto_update_overdue_status(self):
        """
        Cron job to automatically mark invoices as overdue.
        Runs daily to update status based on due dates.
        """
        today = fields.Date.today()
        overdue_invoices = self.search([
            ('due_date', '<', today),
            ('amount_residual', '>', 0),
            ('state', 'in', ['sent', 'partial']),
        ])

        overdue_invoices.write({'state': 'overdue'})
        _logger.info(f'Updated {len(overdue_invoices)} invoices to overdue status')

        return True

    @api.model
    def cron_generate_semester_invoices(self, semester='fall', academic_year='2024-2025'):
        """
        Scheduled action to bulk generate invoices at semester start.

        PERFORMANCE OPTIMIZATION:
        - Batch processes students to avoid memory issues
        - Uses create_multi for efficient bulk creation
        - Single search for all active students
        - Commits in batches to avoid long transactions

        Args:
            semester: 'fall', 'spring', or 'summer'
            academic_year: Academic year string (e.g., '2024-2025')
        """
        # Find all active students
        students = self.env['res.partner'].search([
            ('is_student', '=', True),
            ('active', '=', True),
            ('grade_level', '!=', False)
        ])

        if not students:
            _logger.warning('No students found for invoice generation')
            return True

        _logger.info(f'Starting invoice generation for {len(students)} students')

        invoice_vals_list = []
        created_count = 0
        error_count = 0

        for student in students:
            try:
                # Find applicable fee structures for this student's grade
                fee_structures = self.env['school.fee.structure'].search([
                    ('grade_level', '=', student.grade_level),
                    ('active', '=', True),
                    ('academic_year', '=', academic_year),
                    ('recurrence', 'in', ['one_time', 'semester', 'annual'])
                ])

                if not fee_structures:
                    _logger.warning(f'No fee structures found for student {student.name}, grade {student.grade_level}')
                    continue

                # Create invoice in accounting module
                invoice_line_vals = []
                for fee_struct in fee_structures:
                    final_amount = fee_struct.calculate_final_amount()
                    invoice_line_vals.append((0, 0, {
                        'name': f'{fee_struct.fee_type_id.name} - {semester.title()} Semester',
                        'quantity': 1,
                        'price_unit': final_amount,
                        'tax_ids': [(6, 0, [])],  # No taxes by default
                    }))

                # Create the accounting invoice
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': student.parent_id.id if student.parent_id else student.id,
                    'invoice_date': fields.Date.today(),
                    'invoice_date_due': fields.Date.today() + timedelta(days=30),
                    'invoice_line_ids': invoice_line_vals,
                })

                # Create student invoice record
                invoice_vals_list.append({
                    'student_id': student.id,
                    'invoice_id': invoice.id,
                    'semester': semester,
                    'academic_year': academic_year,
                    'state': 'draft',
                })

                created_count += 1

                # Batch commit every 50 invoices for performance
                if len(invoice_vals_list) >= 50:
                    self.create(invoice_vals_list)
                    self.env.cr.commit()
                    _logger.info(f'Committed batch of {len(invoice_vals_list)} invoices')
                    invoice_vals_list = []

            except Exception as e:
                error_count += 1
                _logger.error(f'Error generating invoice for student {student.name}: {str(e)}')
                continue

        # Create remaining invoices
        if invoice_vals_list:
            self.create(invoice_vals_list)
            self.env.cr.commit()

        _logger.info(
            f'Invoice generation complete. Created: {created_count}, Errors: {error_count}'
        )

        return True

    # SQL constraints for data integrity
    _sql_constraints = [
        ('student_invoice_unique',
         'UNIQUE(student_id, invoice_id)',
         'This invoice is already linked to this student!'),
    ]