from email.policy import default
from tokenize import group

from odoo import models,fields,api
from odoo.api import readonly
from odoo.exceptions import ValidationError

class Property(models.Model):

    _name = 'property'
    _description = 'Property Record'
    _inherit = ['mail.thread','mail.activity.mixin']

    ref = fields.Char(default='New',readonly=True)
    name = fields.Char(default="New", size=14)
    description = fields.Text(tracking=True)
    postcode = fields.Char(required=False)
    date_availability = fields.Date(tracking=True)
    expected_selling_date = fields.Date(tracking=True)
    is_late = fields.Boolean()
    expected_price = fields.Float(digits=(0,2))
    selling_price = fields.Float(groups="app_one.property_manager_group")
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

    owner_address = fields.Char(related='owner_id.address',readonly = False)
    owner_phone = fields.Char(related='owner_id.phone_number',store=True)
    tag_ids = fields.Many2many('tag')
    active=fields.Boolean(default=True)

    line_ids = fields.One2many('property.line','property_id')


    state = fields.Selection([
        ('draft','Draft'),
        ('pending', 'Pending'),
        ('sold','Sold'),
        ('closed','Close'),  #1 in 42 server action
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

    @api.onchange('expected_price','owner_id.phone_number')
    #the field name MUST BE in current model (simple field)  and view only not in (relsted field)related model (owner_id.phone_number) won't work
    def _onchange_expected_price(self):
        for rec in self:
            # print(rec)
            print('inside _onchange_expected_price')


    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state,'draft')
            rec.state = 'draft'

            # rec.write ({
            #
            # })

    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state,'pending')
            rec.state = 'pending'
            # rec.write ({
            #
            # })


    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state,'sold')
            rec.state = 'sold'


    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state,'closed')
            rec.state = 'closed'


    def check_expected_selling_date(self):
        property_ids = self.search([])
        for rec in property_ids:
            if rec.expected_selling_date and rec.expected_selling_date < fields.date.today():
                rec.is_late = True


    # def action(self):
    #     print(self.env['owner'].create({
    #         'name' : 'name one',
    #         'phone_number' : '012544444444',
    #     }))


    def action(self):
        print(self.env['property'].search([
            '|',
            ('name', '!=', 'Property1'),
            ('postcode', '=', '12345')
        ]))

    @api.model
    def create(self, vals):
        res = super(Property,self).create(vals)
        if res.ref == 'New':
          res.ref =  self.env['ir.sequence'].next_by_code('property_seq')
        return res

    def create_history_record(self,old_state,new_state,reason):
        for rec in self:
            rec.env['property.history'].create({
                'user_id':rec.env.uid,
                'property_id':rec.id,
                'old_state':old_state,
                'new_state':new_state,
                'reason':reason or "",
            })

    def action_open_change_state_wizard(self):
        action=self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context'] = {'default_property_id':self.id}
        return action



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


class PropertyLines(models.Model):

    _name = 'property.line'
    area = fields.Float()
    description = fields.Char()
    property_id = fields.Many2one('property')