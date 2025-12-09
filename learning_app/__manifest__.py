{
    'name': "Learning App",
    'author': "Gehad Baleegh",
    'category': 'School',
    'version': '18.0.0.1.0',  # recommended Odoo version format ( 18.0.0 odooVersion and 1.0 app version )
    'depends': [
        'base',
    ],
    'data': [
        # add your XML files here later
        'views/base_menu.xml',
        'views/course_view.xml',
        'views/student_view.xml',
        'views/teacher_view.xml',
        # 'views/enrollment_view.xml',
        'security/ir.model.access.csv',

    ],
    'application': True,
}
