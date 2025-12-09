from odoo import models,fields,api
from odoo.exceptions import ValidationError

class Property(models.Model):

    _name = 'property'

    name = fields.Char(default="New", size=14)
    description = fields.Text()
    postcode = fields.Char(required=True)
    date_availability = fields.Date()
    expected_price = fields.Float(digits=(0,4))
    selling_price = fields.Float()
    bed_rooms = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_oreintation = fields.Selection([
        ('north','North'),
        #dtabase_name --> north  , #UI_name(what user see) --> North
        ('south','South'),
        ('east','East'),
        ('west','West'),
    ])

    owner_id = fields.Many2one('owner')
    tag_ids = fields.Many2many('tag')

    _sql_constraints = [
        ('name_unique','UNIQUE("name")',('Name already exists!'))
    ]


    # @api.constrains('bed_rooms')
    # def _check_not_equal_zerp(self):
    #     # for rec in self:         # without for it is called record set return more than one record
    #     #     if rec.bed_rooms == 0:
    #     if self.bed_rooms == 0:
    #         raise ValidationError('please add valid number to beadrooms')

    @api.constrains('bed_rooms')
    def _check_not_equal_zero(self):
        for rec in self:         # without for it is called record set return more than one record
            if rec.bed_rooms == 0:
                     raise ValidationError('please add valid number to beadrooms')

    #
    #
    # @api.model_create_multi  #create
    # def create(self,vals):
    #     res = super(Property,self).create(vals)
    #     print("inside create method")
    #     return res
    #
    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None):
    #     res = super()._search(
    #         domain=domain,
    #         offset=offset,
    #         limit=limit,
    #         order=order
    #     )
    #     print("inside search method")
    #     return res
    #
    #
    #
    #
    # def write(self, vals):  #update
    #     res = super(Property,self).write(vals)
    #     print('inside write method')
    #     return  res
    #
    # def unlink(self):
    #     print("Inside unlink method. Records to delete:", self)
    #     res = super(Property, self).unlink()  # call the real unlink
    #     print("After unlink")
    #     return res
