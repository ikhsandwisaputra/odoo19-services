# -*- coding: utf-8 -*-
from odoo import models, fields

class ClientCompany(models.Model):
    # Nama teknis model (tabel di database)
    _name = 'client.company' 
    _description = 'Data Perusahaan Klien'

    # Definisikan kolom-kolomnya
    name = fields.Char(string="Nama Perusahaan", required=True)
    phone = fields.Char(string="Telepon Perusahaan")
    email = fields.Char(string="Email Perusahaan")

    # --- INI BAGIAN PENTING ---
    # Kita membuat relasi Many2one (Banyak ke Satu) ke model 'res.partner'
    # 'res.partner' adalah model yang digunakan oleh aplikasi Contacts.
    contact_person_id = fields.Many2one(
        'res.partner',  # Model target (Contacts)
        string="Kontak PIC",
        help="Pilih kontak dari aplikasi Contacts yang ada."
    )
    # ---------------------------