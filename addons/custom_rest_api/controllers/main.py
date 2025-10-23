import json
from odoo import http
from odoo.http import request, Response

class ContactAPI(http.Controller):
    
    # === PENGATURAN & HELPER ===
    
    # Ganti dengan origin frontend Anda (misal: port React/Vue)
    # Gunakan '*' hanya untuk pengembangan, jangan di produksi.
    _cors_origin = 'http://localhost:5173'
    
    # Daftar field yang diizinkan untuk dibuat (Create) atau diubah (Update)
    # Ini adalah "best practice" keamanan untuk mencegah mass-assignment.
    # Jangan izinkan field sensitif seperti 'is_admin', dll.
    _allowed_fields = ['name', 'email', 'phone', 'street', 'city', 'zip', 'country_id', 'company_id']

    def _get_cors_headers(self, methods='GET, OPTIONS'):
        """Helper untuk menghasilkan header CORS."""
        return {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': self._cors_origin,
            'Access-Control-Allow-Methods': methods,
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true', # Jika Anda menggunakan auth='user'
        }

    def _format_partner_data(self, partner):
        """Helper untuk memformat data partner ke dict."""
        if not partner or not partner.exists():
            return {}
        return {
            'id': partner.id,
            'name': partner.name,
            'email': partner.email,
            'phone': partner.phone,
            'company_name': partner.company_id.name if partner.company_id else None,
            'street': partner.street,
            'city': partner.city,
            'zip': partner.zip,
            'country': partner.country_id.name if partner.country_id else None,
        }

    def _validate_and_sanitize_data(self, data):
        """
        Memfilter data JSON yang masuk agar hanya field yang
        diizinkan dalam '_allowed_fields' yang diproses.
        """
        clean_data = {}
        for field in self._allowed_fields:
            if field in data:
                clean_data[field] = data[field]
        
        # Di sini Anda bisa menambahkan validasi lebih lanjut,
        # misalnya: mengecek format email, dll.
        
        return clean_data

    def _make_json_response(self, data, status=200, headers={}):
        """Helper untuk membuat response JSON terstandardisasi."""
        return Response(
            json.dumps(data),
            status=status,
            headers=headers
        )

    # === ENDPOINT CRUD ===
    
    # 1. CREATE (POST) & READ ALL (GET)
    @http.route('/api/contacts', 
              type='http', 
              # PENTING: 'auth="public"' tidak aman untuk produksi!
              # Ini mengizinkan siapa saja (tanpa login) untuk mengakses data.
              # Ganti ke auth="user" untuk produksi.
              auth='public', 
              methods=['GET', 'POST', 'OPTIONS'], 
              csrf=False)
    def handle_contacts(self, **kw):
        """
        Endpoint untuk GET (semua kontak) dan POST (buat kontak baru).
        """
        # Tentukan metode apa saja yang diizinkan di endpoint ini
        methods_allowed = 'GET, POST, OPTIONS'
        headers = self._get_cors_headers(methods=methods_allowed)
        
        # Handle pre-flight OPTIONS request dari browser
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)
        
        # === CREATE (POST) ===
        if request.httprequest.method == 'POST':
            try:
                # 1. Ambil data JSON dari body request
                payload = json.loads(request.httprequest.data.decode('utf-8'))
                
                # 2. Validasi dan bersihkan data
                clean_data = self._validate_and_sanitize_data(payload)
                
                # 3. (Opsional) Validasi data minimum (contoh: 'name' wajib ada)
                if not clean_data.get('name'):
                    return self._make_json_response(
                        {'error': 'Field "name" wajib diisi.'}, 
                        status=400, headers=headers
                    )

                # 4. Buat record baru
                new_partner = request.env['res.partner'].sudo().create(clean_data)
                
                # 5. Format data balikan
                formatted_data = self._format_partner_data(new_partner)
                
                # 6. Kirim response 201 Created
                return self._make_json_response(
                    {'data': formatted_data, 'message': 'Kontak baru berhasil dibuat.'}, 
                    status=201, # 201 Created lebih cocok untuk POST
                    headers=headers
                )
            
            except json.JSONDecodeError:
                return self._make_json_response(
                    {'error': 'Format JSON tidak valid.'}, 
                    status=400, headers=headers
                )
            except Exception as e:
                # Tangani error Odoo (misal: field unik terduplikasi)
                return self._make_json_response(
                    {'error': str(e), 'message': 'Gagal membuat kontak.'}, 
                    status=500, headers=headers
                )
        
        # === READ ALL (GET) ===
        if request.httprequest.method == 'GET':
            try:
                # Cari semua partner, Anda bisa menambahkan domain filter di sini
                # contoh: domain = [('is_company', '=', True)]
                domain = []
                partners = request.env['res.partner'].sudo().search(domain)
                
                # Format data menggunakan list comprehension
                data = [self._format_partner_data(p) for p in partners]
                
                response_data = {'count': len(data), 'data': data}
                return self._make_json_response(response_data, status=200, headers=headers)
                
            except Exception as e:
                return self._make_json_response(
                    {'error': str(e)}, 
                    status=500, headers=headers
                )

    # 2. READ (by ID), UPDATE, DELETE
    @http.route('/api/contacts/<int:partner_id>', 
              type='http', 
              auth='public', # PENTING: Ganti ke auth="user" untuk produksi
              methods=['GET', 'PUT', 'DELETE', 'OPTIONS'], 
              csrf=False)
    def handle_contact_by_id(self, partner_id, **kw):
        """
        Endpoint untuk GET (satu kontak), PUT (update), DELETE (hapus)
        berdasarkan ID.
        """
        methods_allowed = 'GET, PUT, DELETE, OPTIONS'
        headers = self._get_cors_headers(methods=methods_allowed)

        # Handle pre-flight OPTIONS
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)

        # Cek apakah partner ada
        try:
            # .sudo() digunakan di sini agar bisa diakses oleh method lain (PUT, DELETE)
            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                return self._make_json_response(
                    {'error': 'Kontak tidak ditemukan.'}, 
                    status=404, headers=headers
                )
        except Exception as e:
             return self._make_json_response(
                {'error': str(e), 'message': 'Error saat mencari kontak.'}, 
                status=500, headers=headers
            )

        # === READ BY ID (GET) ===
        if request.httprequest.method == 'GET':
            formatted_data = self._format_partner_data(partner)
            return self._make_json_response({'data': formatted_data}, status=200, headers=headers)

        # === UPDATE (PUT) ===
        if request.httprequest.method == 'PUT':
            try:
                payload = json.loads(request.httprequest.data.decode('utf-8'))
                clean_data = self._validate_and_sanitize_data(payload)
                
                if not clean_data:
                    return self._make_json_response(
                        {'error': 'Tidak ada data valid untuk diupdate.'}, 
                        status=400, headers=headers
                    )

                partner.write(clean_data)
                updated_data = self._format_partner_data(partner)
                return self._make_json_response(
                    {'data': updated_data, 'message': 'Kontak berhasil diperbarui.'}, 
                    status=200, headers=headers
                )
            except Exception as e:
                return self._make_json_response({'error': str(e)}, status=500, headers=headers)


        # === DELETE (DELETE) ===
        if request.httprequest.method == 'DELETE':
            try:
                partner_name = partner.name # Simpan nama untuk pesan balikan
                
                # Hapus record (partner sudah mengandung .sudo())
                partner.unlink() 
                
                return self._make_json_response(
                    {'message': f'Kontak "{partner_name}" (ID: {partner_id}) berhasil dihapus.'},
                    status=200, headers=headers # 200 OK (bukan 204) agar bisa kirim body
                )
            except Exception as e:
                # Tangani jika record tidak bisa dihapus (misal: karena relasi)
                return self._make_json_response(
                    {'error': str(e), 'message': 'Gagal menghapus kontak.'}, 
                    status=500, headers=headers
                )
