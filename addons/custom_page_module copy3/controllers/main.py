# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CustomWebPage(http.Controller):

    @http.route('/halaman-custom-saya', type='http', auth='public', website=True)
    def show_custom_page(self, **kw):
        """
        PERUBAHAN:
        Kita tidak perlu lagi mengambil data produk di sini.
        Halaman ini sekarang hanya menjadi 'cangkang' kosong
        yang bisa diisi dengan snippet.
        Snippet akan mengambil datanya sendiri.
        """
        
        # Kita hanya me-render 'cangkang' halamannya
        return request.render('custom_page_module.template_halaman_kustom', {})

