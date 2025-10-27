{
    'name': 'Modul Halaman Kustom',
    'version': '1.0',
    # ... (deskripsi bisa Anda update) ...
    'author': 'Nama Anda',
    'website': 'https://website-anda.com',
    'category': 'Website',
    'depends': [
        'base',
        'website',
        'product',  
    ],
    'data': [
        'views/templates.xml',
        'views/snippets.xml', # <-- TAMBAHKAN FILE BARU INI
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

