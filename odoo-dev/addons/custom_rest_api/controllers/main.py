import json
from odoo import http
from odoo.http import request, Response

class ContactAPI(http.Controller):
    
    @http.route('/api/contacts', 
              type='http', 
              # 1. 'auth' diubah ke 'public' untuk tes (bypass login Odoo)
              #    PERINGATAN: Ini tidak aman untuk data sensitif di produksi.
              auth='public', 
              
              # 2. Tambahkan 'OPTIONS' untuk menangani "pre-flight request" dari browser
              methods=['GET', 'OPTIONS'], 
              
              csrf=False)
    def get_contacts(self, **kw):
        """
        Endpoint untuk mengambil semua data kontak (res.partner).
        """
        
        # 3. Definisikan header CORS
        #    Ini memberitahu browser bahwa 'http://localhost:5173' diizinkan.
        #    Ganti URL ini jika port React Anda berbeda.
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'http://localhost:5173', 
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
        
        # 4. Tangani request OPTIONS (pre-flight)
        #    Browser mengirim ini SEBELUM request GET untuk mengecek izin CORS.
        if request.httprequest.method == 'OPTIONS':
            # Langsung kembalikan response OK dengan headers
            return Response(status=200, headers=headers)
            
        # --- Logika GET Anda ---
        try:
            # Cari semua data partner (kontak)
            partners = request.env['res.partner'].sudo().search([])
            
            # Siapkan data untuk output JSON
            data = []
            for p in partners:
                data.append({
                    'id': p.id,
                    'name': p.name,
                    'email': p.email,
                    'phone': p.phone,
                    'company_name': p.company_id.name if p.company_id else None,
                })
            
            response_data = {
                'count': len(data),
                'data': data
            }
            
            # 5. Kembalikan response SUKSES dengan headers CORS
            return Response(
                json.dumps(response_data),
                status=200,
                headers=headers
            )
            
        except Exception as e:
            # 6. Kembalikan response ERROR dengan headers CORS
            #    (Ini penting agar React bisa membaca pesan error-nya)
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                headers=headers
            )
