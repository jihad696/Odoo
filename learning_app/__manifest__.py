# __manifest__.py
{
    'name': 'School Management',
    'version': '1.0',
    # 'summary': 'School Management System',
    'category': 'Education',
    'author': 'G',
    # 'website': 'https://www.example.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/base_menu.xml',
        'views/student_view.xml',
        'views/teacher_view.xml',
        'views/course_view.xml',
    ],
    'demo': [],
    'application': True,

}