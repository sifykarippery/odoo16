# -*- coding: utf-8 -*-
{
    'name': "custom_module",

    'summary': """
        Attendance Base On Project And Task""",

    'description': """
        Odoo employees can choose the project and task,update description while filling out the HR Attendance Check In/out
    """,

    'author': "Sify Karippery Raphy",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','hr','project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
'assets': {
        'web.assets_backend': [
            'custom_module/static/src/js/my_attendance_inherit.js',
            'custom_module/static/src/xml/my_attendance_inherit.xml',
        ],

    },
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'license': 'LGPL-3',

}
