from odoo import models,fields,api
from odoo.exceptions import ValidationError

class Property(models.Model):

    _name = 'property'

    name = fields.Char(default="New", size=14)
    description = fields.Text()
    postcode = fields.Char(required=True)
    date_availability = fields.Date()
    expected_price = fields.Float(digits=(0,2))
    selling_price = fields.Float()
    diff = fields.Float(compute='_compute_diff',store=True)
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
    state = fields.Selection([
        ('draft','Draft'),
        ('pending', 'Pending'),
        ('sold','Sold'),
    ],default='draft')

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


    @api.depends('expected_price','selling_price','owner_id.phone_number')
    def _compute_diff(self):
        for rec in self:
            print(rec)
            print('inside compute_diff method')
            rec.diff = rec.expected_price - rec.selling_price

    @api.onchange('expected_price','owner_id.phone_number')  #the field name MUST BE in current model (simple field)  and view only not in (relsted field)related model (owner_id.phone_number) won't work
    def _onchange_expected_price(self):
        for rec in self:
            # print(rec)
            print('inside _onchange_expected_price')


    def action_draft(self):
        for rec in self:
            print("inside draft action")
            rec.state = 'draft'
            # rec.write ({
            #
            # })

    def action_pending(self):
        for rec in self:
            print("inside pending action")
            rec.state = 'pending'
            # rec.write ({
            #
            # })


    def action_sold(self):
        for rec in self:
            print("inside sold action")
            rec.state = 'sold'
            # rec.write ({
            #
            # })


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
