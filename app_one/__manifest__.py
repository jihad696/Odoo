{
    'name': "App One",
    'author': "Gehad Baleegh",
    'category': '',
    'version': '18.0.0.1.0',  # recommended Odoo version format ( 18.0.0 odooVersion and 1.0 app version )
    'depends': [
        'base','sale_management','account'
    ],
    'data': [
        # add your XML files here later (paths)

        'views/base_menu.xml',
        'views/property_view.xml',
        'views/owner_view.xml',
        'views/tags_view.xml',
        'views/sale_order_view.xml',
        'security/ir.model.access.csv',

    ],
    'assets': {
        'web.assets_backend': ['app_one/static/src/property.css']
    },
    'application': True,
}
#