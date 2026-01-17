# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    """
    Extend account.move to link invoices with student records.
    This provides bidirectional navigation between accounting and school modules.
    """
    _inherit = 'account.move'

    student_invoice_id = fields.Many2one(
        'school.student.invoice',
        string='Student Invoice',
        copy=False,
        index=True  # INDEX: Fast lookup from accounting module
    )

    is_school_invoice = fields.Boolean(
        string='Is School Invoice',
        compute='_compute_is_school_invoice',
        store=True,
        index=True  # INDEX: Fast filtering of school invoices
    )

    @api.depends('student_invoice_id')
    def _compute_is_school_invoice(self):
        """Flag to identify school-related invoices"""
        for move in self:
            move.is_school_invoice = bool(move.student_invoice_id)

    def action_view_student_invoice(self):
        """Quick action to view related student invoice"""
        self.ensure_one()
        if not self.student_invoice_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'school.student.invoice',
            'view_mode': 'form',
            'res_id': self.student_invoice_id.id,
            'target': 'current',
        }