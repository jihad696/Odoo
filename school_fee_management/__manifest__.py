# -*- coding: utf-8 -*-
{
    'name': 'School Fee Management',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Manage student fees, invoices, and payments with parent portal',
    'description': """
        School Fee Management System
        =============================
        * Define fee structures by grade level
        * Automated invoice generation
        * Payment tracking and history
        * Parent portal for invoice viewing
        * Performance optimized with proper indexing
        * Complete audit trail
        * Multi-level security implementation
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'account',  # Odoo Invoicing module
        'mail',  # For message tracking and audit trail
    ],
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

        # Data
        'data/fee_type_data.xml',
        'data/cron_jobs.xml',
        'data/demo_data.xml',

        # Views
        'views/fee_structure_views.xml',
        'views/student_invoice_views.xml',
        'views/payment_transaction_views.xml',
        'views/parent_portal_views.xml',
        'views/menu_items.xml',

        # Reports
        'reports/outstanding_payments_report.xml',
        'reports/revenue_summary_report.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}