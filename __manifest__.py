{
    'name': 'Prestamos',
    'version': '1.2',
    'summary': 'Prestamos',
    'description': "",
    'website': 'https://www.google.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/loan_request_views.xml',
        'views/loan_views.xml',
        'views/loan_menu.xml',
        'views/loan_expense_views.xml',
        'views/loan_cashflow_views.xml',
        'views/loan_balance_views.xml',
        'views/loan_menu.xml',
    ],
    "assets": {
        
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
