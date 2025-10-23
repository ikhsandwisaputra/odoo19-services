{
    'name': "Custom REST API",
    'version': '1.0',
    'summary': 'Provides a simple REST API for contacts',
    'description': """
        Modul ini menambahkan endpoint REST API untuk mengambil data kontak (res.partner).
    """,
    'author': "Anda",
    'category': 'Tools',
    'depends': [
        'base',      # Selalu dibutuhkan
        'contacts',  # Karena kita akan mengambil data dari modul Contacts
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}