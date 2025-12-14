{
    'name': "To Do Modules",
    'author': "Gehad Baleegh",
    'category': 'to do',
    'version': '18.0.0.1.0',  # recommended Odoo version format ( 18.0.0 odooVersion and 1.0 app version )
    'depends': [
        'base',
    ],
    'data': [

        # add your XML files here later

        'views/base_view.xml',
        'views/todo_view.xml',
        'security/ir.model.access.csv',


    ],

    'application': True,
}
