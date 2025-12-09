from odoo import models



class ModelC(models.AbstractModel):  # it won't be added in database cuz it is abstract 
    _name = 'model.c'