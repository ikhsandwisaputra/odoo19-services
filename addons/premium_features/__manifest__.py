{
    'name': 'Premium Feature',
    'version': '1.0',
    'category': 'Extra Tools',
    'summary': 'Premium Feature - Upgrade Required',
    'description': """
        This is a premium feature that requires an upgrade.
        Click 'Learn More' to see feature details or 'Upgrade' to unlock this feature.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/premium_feature_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'premium_feature/static/src/css/premium_feature.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
