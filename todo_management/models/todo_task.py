from odoo import models, fields




class ResUser(models.Model):
    _inherit = 'res.users'



class ToDoTask(models.Model):
    _name = 'todo.task'
    _description = 'To Do Task'

    name = fields.Char(required=True)
    user_id = fields.Many2one(
        'res.users', string='Assigned To'
    )
    description = fields.Text()
    due_date = fields.Date()
    status = fields.Selection(
        [('new', 'New'), ('in_progress', 'In Progress'), ('done', 'Completed')],
        default='new'
    )

    username = fields.Char(
        string='Username',
        related='user_id.login',
        store=True,
        index=True  # make it searchable
    )
