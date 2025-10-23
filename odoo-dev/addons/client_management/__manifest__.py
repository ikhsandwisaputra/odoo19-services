# -*- coding: utf-8 -*-
{
    'name': "Manajemen Klien",
    'version': '1.0',
    'summary': "Modul untuk mengelola data perusahaan klien.",
    'description': """
        Modul sederhana untuk mencatat data perusahaan klien,
        termasuk nama perusahaan dan kontak PIC yang diambil
        dari aplikasi Contacts (res.partner).
    """,
    'author': "Nama Anda", # Ganti dengan nama Anda
    'website': "https://www.website-anda.com", # Opsional
    'category': 'Sales/CRM',
    
    # Kunci utamanya ada di 'depends'
    # Kita perlu modul 'contacts' agar bisa terhubung ke datanya.
    'depends': [
        'base', 
        'contacts'
    ],
    
    # Data yang akan di-load (views dan security)
    'data': [
        'security/ir.model.access.csv',
        'views/client_company_views.xml',
    ],
    
    'installable': True,
    'application': True, # Jadikan ini sebagai "Aplikasi" di menu Apps Odoo
    'auto_install': False,
}