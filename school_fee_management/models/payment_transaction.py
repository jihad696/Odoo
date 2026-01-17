# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    """
    Tracks all payment transactions for student invoices.
    Provides a complete payment history timeline.

    OPTIMIZATION:
    - student_invoice_id indexed for fast payment history retrieval
    - payment_date indexed for chronological sorting and date range queries
    - Denormalized student_id for direct access without joins

    WHY THIS MODEL?
    - Complete audit trail of all payment attempts
    - Support for partial payments
    - Track payment methods and references
    - Historical record even if invoice is deleted (if needed)
    """
    _name = 'school.payment.transaction'
    _description = 'Payment Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payment_date desc, id desc'

    name = fields.Char(
        string='Transaction Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    student_invoice_id = fields.Many2one(
        'school.student.invoice',
        string='Student Invoice',
        required=True,
        ondelete='cascade',
        index=True,  # INDEX: Fast payment history lookup
        tracking=True
    )

    # Denormalized for performance
    student_id = fields.Many2one(
        'res.partner',
        string='Student',
        related='student_invoice_id.student_id',
        store=True,
        index=True,  # INDEX: Fast filtering by student
        readonly=True
    )

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        related='student_invoice_id.invoice_id',
        store=True,
        readonly=True
    )

    payment_date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.context_today,
        index=True,  # INDEX: Fast chronological queries
        tracking=True
    )

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

    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('online', 'Online Payment'),
        ('other', 'Other'),
    ], string='Payment Method', required=True, default='cash', tracking=True)

    payment_reference = fields.Char(
        string='Payment Reference',
        help='Check number, transaction ID, etc.',
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('reconciled', 'Reconciled'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Link to actual accounting payment if reconciled
    account_payment_id = fields.Many2one(
        'account.payment',
        string='Account Payment',
        readonly=True,
        ondelete='set null'
    )

    notes = fields.Text(string='Notes')

    # Computed fields for validation
    invoice_amount_due = fields.Monetary(
        string='Invoice Amount Due',
        related='student_invoice_id.amount_residual',
        readonly=True
    )

    @api.model
    def create(self, vals):
        """Generate unique transaction reference on creation"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('school.payment.transaction') or _('New')
        return super().create(vals)

    @api.constrains('amount')
    def _check_amount(self):
        """Validate payment amount"""
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Payment amount must be greater than zero.'))

            # Warning if payment exceeds due amount (but allow it for overpayment/credit)
            if record.amount > record.invoice_amount_due:
                _logger.warning(
                    f'Payment amount ({record.amount}) exceeds invoice due amount '
                    f'({record.invoice_amount_due}) for transaction {record.name}'
                )

    @api.constrains('payment_date', 'student_invoice_id')
    def _check_payment_date(self):
        """Validate payment date is not before invoice date"""
        for record in self:
            if record.student_invoice_id.invoice_date and record.payment_date < record.student_invoice_id.invoice_date:
                raise ValidationError(_('Payment date cannot be before invoice date.'))

    def action_confirm(self):
        """
        Confirm payment transaction.
        This validates the payment but doesn't reconcile it yet.
        """
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('Only draft transactions can be confirmed.'))

            record.write({'state': 'confirmed'})
            record.message_post(
                body=_('Payment of %s confirmed by %s') % (
                    record.amount,
                    self.env.user.name
                ),
                subject=_('Payment Confirmed')
            )

            # Update invoice state if fully paid
            if record.student_invoice_id.amount_residual <= 0:
                record.student_invoice_id.write({'state': 'paid'})
            elif record.student_invoice_id.state in ['sent', 'overdue']:
                record.student_invoice_id.write({'state': 'partial'})

    def action_reconcile(self):
        """
        Reconcile payment with accounting invoice.
        This creates the actual account.payment record.
        """
        self.ensure_one()
        if self.state != 'confirmed':
            raise ValidationError(_('Only confirmed transactions can be reconciled.'))

        # Create accounting payment
        payment_vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.student_id.id,
            'amount': self.amount,
            'date': self.payment_date,
            'ref': self.name,
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
        }

        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        # Reconcile with invoice
        payment_lines = payment.line_ids.filtered(
            lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable'))
        invoice_lines = self.invoice_id.line_ids.filtered(
            lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable'))
        (payment_lines + invoice_lines).reconcile()

        self.write({
            'state': 'reconciled',
            'account_payment_id': payment.id
        })

        self.message_post(
            body=_('Payment reconciled with invoice. Payment ID: %s') % payment.name,
            subject=_('Payment Reconciled')
        )

    def action_cancel(self):
        """Cancel payment transaction with audit trail"""
        for record in self:
            if record.state == 'reconciled':
                raise ValidationError(_('Cannot cancel a reconciled payment. Please unrec oncile first.'))

            record.write({'state': 'cancelled'})
            record.message_post(
                body=_('Payment cancelled by %s') % self.env.user.name,
                subject=_('Payment Cancelled')
            )

    def action_reset_to_draft(self):
        """Reset to draft for corrections"""
        for record in self:
            if record.state == 'reconciled':
                raise ValidationError(_('Cannot reset a reconciled payment. Please unreconcile first.'))

            record.write({'state': 'draft'})

    # SQL constraints
    _sql_constraints = [
        ('amount_positive', 'CHECK(amount > 0)', 'Payment amount must be positive!'),
    ]