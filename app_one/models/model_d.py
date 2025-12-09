from odoo import models



class ModelD(models.Model):
    _name = 'model.d'
    _log_access = False    # remove default columns (if you don't need to track the logs who and when and what they did