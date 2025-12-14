{
    'name': "App One",
    'author': "Gehad Baleegh",
    'category': '',
    'version': '18.0.0.1.0',  # recommended Odoo version format ( 18.0.0 odooVersion and 1.0 app version )
    'depends': [
        'base','sale_management','account','mail','contacts'
    ],
    'data': [
        # add your XML files here later (paths)
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/property_view.xml',
        'views/owner_view.xml',
        'views/tags_view.xml',
        'views/sale_order_view.xml',
        'views/res_partner.xml',
        'views/building_view.xml',
        'reports/property_report.xml',


    ],
    'assets': {
        'web.assets_backend': ['app_one/static/src/property.css']
    },
    'application': True,
}
#