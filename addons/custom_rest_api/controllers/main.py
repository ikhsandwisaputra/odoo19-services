import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class ContactAPI(http.Controller):
    
    # === PENGATURAN & HELPER ===
    
    # Ganti dengan origin frontend Anda (misal: port React/Vue)
    # Gunakan '*' hanya untuk pengembangan, jangan di produksi.
    _cors_origin = 'http://localhost:5173'

class EmployeeAPI(http.Controller):
    """API Controller untuk mengakses data karyawan dengan keamanan yang ketat."""
    
    _cors_origin = 'http://localhost:5173'
    
    # Daftar field yang aman untuk ditampilkan
    # Hindari field sensitif seperti bank_account_id, private_email, dll
    _safe_fields = [
        'id', 'name', 'work_email', 'work_phone', 
        'job_title', 'department_id', 'company_id',
        'work_location_id', 'employee_type',
        'job_id', 'resource_calendar_id', 'parent_id'
    ]
    
    def _get_cors_headers(self, methods='GET, OPTIONS'):
        """Helper untuk menghasilkan header CORS yang aman."""
        return {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': self._cors_origin,
            'Access-Control-Allow-Methods': methods,
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'X-Content-Type-Options': 'nosniff',  # Mencegah MIME-sniffing
            'X-Frame-Options': 'DENY',  # Mencegah clickjacking
            'X-XSS-Protection': '1; mode=block'  # Proteksi XSS
        }
    
    def _format_employee_data(self, employee):
        """
        Helper untuk memformat data karyawan ke dict dengan memperhatikan keamanan.
        Hanya mengembalikan field yang sudah didefinisikan sebagai aman.
        """
        if not employee or not employee.exists():
            return {}
            
        data = {
            'id': employee.id,
            'name': employee.name,
            'work_email': employee.work_email or None,
            'work_phone': employee.work_phone or None,
            'job_title': employee.job_title or None,
            'department': employee.department_id.name if employee.department_id else None,
            'company': employee.company_id.name if employee.company_id else None,
            'work_location': employee.work_location_id.name if employee.work_location_id else None,
            'employee_type': employee.employee_type or None,
            'job_position': employee.job_id.name if employee.job_id else None,
            'work_schedule': employee.resource_calendar_id.name if employee.resource_calendar_id else None,
            'manager': {
                'id': employee.parent_id.id,
                'name': employee.parent_id.name
            } if employee.parent_id else None
        }
        
        return data
    
    def _make_json_response(self, data, status=200, headers={}):
        """Helper untuk membuat response JSON yang aman."""
        # Tambahkan header keamanan default
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
        headers.update(security_headers)
        
        return Response(
            json.dumps(data),
            status=status,
            headers=headers
        )

    # === ENDPOINT EMPLOYEES ===
    
    @http.route('/api/employees', 
              type='http', 
              # Gunakan auth='user' untuk memastikan hanya user yang terautentikasi
              auth='public',
              methods=['GET', 'OPTIONS'], 
              csrf=False)
    def get_employees(self, **kw):
        """
        Endpoint untuk mendapatkan daftar karyawan dengan filter dan paginasi.
        Memerlukan autentikasi dan memiliki pembatasan akses.
        
        Query parameters:
        - limit: jumlah maksimum data yang dikembalikan
        - offset: index awal untuk paginasi
        - department: filter berdasarkan departemen
        - company: filter berdasarkan perusahaan
        - active: filter berdasarkan status aktif
        """
        headers = self._get_cors_headers(methods='GET, OPTIONS')
        
        # Handle pre-flight OPTIONS request
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)
            
        try:
            # Verifikasi akses pengguna
            if not request.env.user.has_group('hr.group_hr_user'):
                return self._make_json_response(
                    {'error': 'Akses ditolak. Anda tidak memiliki izin yang diperlukan.'}, 
                    status=403, headers=headers
                )
            
            # Persiapkan domain pencarian
            domain = []
            
            # Filter berdasarkan departemen
            if kw.get('department'):
                domain.append(('department_id.name', 'ilike', kw.get('department')))
            
            # Filter berdasarkan perusahaan
            if kw.get('company'):
                domain.append(('company_id.name', 'ilike', kw.get('company')))
            
            # Filter berdasarkan status aktif
            if 'active' in kw:
                domain.append(('active', '=', kw.get('active').lower() == 'true'))
            
            # Ambil parameter paginasi
            try:
                limit = min(int(kw.get('limit', 50)), 100)  # Batasi maksimum 100 record
                offset = max(int(kw.get('offset', 0)), 0)  # Pastikan offset tidak negatif
            except ValueError:
                return self._make_json_response(
                    {'error': 'Parameter limit dan offset harus berupa angka.'}, 
                    status=400, headers=headers
                )
            
            # Ambil data karyawan dengan sudo() terbatas
            Employee = request.env['hr.employee'].sudo().with_context(active_test=True)
            employees = Employee.search(domain, limit=limit, offset=offset)
            
            # Format data karyawan
            data = [self._format_employee_data(emp) for emp in employees]
            
            # Hitung total untuk paginasi
            total_count = Employee.search_count(domain)
            
            response_data = {
                'count': len(data),
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'data': data
            }
            
            return self._make_json_response(response_data, status=200, headers=headers)
            
        except Exception as e:
            # Log error untuk monitoring
            _logger.error("Error in get_employees: %s", str(e))
            return self._make_json_response(
                {'error': 'Terjadi kesalahan internal server.'}, 
                status=500, headers=headers
            )

    @http.route('/api/employees/<int:employee_id>', 
              type='http', 
              auth='public',
              methods=['GET', 'OPTIONS'], 
              csrf=False)
    def get_employee_by_id(self, employee_id, **kw):
        """
        Endpoint untuk mendapatkan detail satu karyawan berdasarkan ID.
        Memerlukan autentikasi dan memiliki pembatasan akses.
        """
        headers = self._get_cors_headers(methods='GET, OPTIONS')

        # Handle pre-flight OPTIONS
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)

        try:
            # Verifikasi akses pengguna
            if not request.env.user.has_group('hr.group_hr_user'):
                return self._make_json_response(
                    {'error': 'Akses ditolak. Anda tidak memiliki izin yang diperlukan.'}, 
                    status=403, headers=headers
                )

            employee = request.env['hr.employee'].sudo().browse(employee_id)
            if not employee.exists():
                return self._make_json_response(
                    {'error': 'Karyawan tidak ditemukan.'}, 
                    status=404, headers=headers
                )

            # Periksa akses ke perusahaan karyawan (jika berbeda perusahaan)
            if employee.company_id and employee.company_id != request.env.user.company_id:
                if not request.env.user.has_group('hr.group_hr_manager'):
                    return self._make_json_response(
                        {'error': 'Akses ditolak. Anda tidak memiliki izin untuk melihat data karyawan dari perusahaan lain.'}, 
                        status=403, headers=headers
                    )

            formatted_data = self._format_employee_data(employee)
            return self._make_json_response(
                {'data': formatted_data}, 
                status=200, headers=headers
            )

        except Exception as e:
            # Log error untuk monitoring
            _logger.error("Error in get_employee_by_id: %s", str(e))
            return self._make_json_response(
                {'error': 'Terjadi kesalahan internal server.'}, 
                status=500, headers=headers
            )

class CompanyAPI(http.Controller):
    """API Controller untuk mengambil data perusahaan (GET only).

    Endpoints:
    - GET /api/companies
    - GET /api/companies/<id>

    Security: requires auth='user' (logged in). Responses include safe fields
    and CORS/security headers. Pagination and simple filters supported.
    """

    _cors_origin = 'http://localhost:5173'

    def _get_cors_headers(self, methods='GET, OPTIONS'):
        return {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': self._cors_origin,
            'Access-Control-Allow-Methods': methods,
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
        }

    def _format_company_data(self, company):
        if not company or not company.exists():
            return {}
        return {
            'id': company.id,
            'name': company.name,
            'street': getattr(company, 'street', None),
            'city': getattr(company, 'city', None),
            'zip': getattr(company, 'zip', None),
            'phone': getattr(company, 'phone', None),
            'email': getattr(company, 'email', None),
            'website': getattr(company, 'website', None),
            'country': company.country_id.name if getattr(company, 'country_id', None) else None,
            'currency': company.currency_id.name if getattr(company, 'currency_id', None) else None,
            'active': getattr(company, 'active', True),
        }

    def _make_json_response(self, data, status=200, headers={}):
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
        headers.update(security_headers)
        return Response(json.dumps(data), status=status, headers=headers)

    @http.route('/api/companies',
              type='http',
              auth='user',
              methods=['GET', 'OPTIONS'],
              csrf=False)
    def get_companies(self, **kw):
        """Return list of companies. Query params: limit, offset, name, active."""
        headers = self._get_cors_headers(methods='GET, OPTIONS')
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)

        try:
            # basic domain
            domain = []
            if kw.get('name'):
                domain.append(('name', 'ilike', kw.get('name')))
            if 'active' in kw:
                domain.append(('active', '=', kw.get('active').lower() == 'true'))

            # pagination
            try:
                limit = int(kw.get('limit', 0)) if kw.get('limit') else 0
            except Exception:
                limit = 0
            try:
                offset = max(int(kw.get('offset', 0)), 0)
            except Exception:
                offset = 0

            Company = request.env['res.company'].sudo()
            companies = Company.search(domain, limit=(limit or 0), offset=offset)

            data = [self._format_company_data(c) for c in companies]
            total_count = Company.search_count(domain)

            response_data = {
                'count': len(data),
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'data': data,
            }
            return self._make_json_response(response_data, status=200, headers=headers)
        except Exception as e:
            _logger.error('Error in get_companies: %s', e)
            return self._make_json_response({'error': 'Internal server error.'}, status=500, headers=headers)

    @http.route('/api/companies/<int:company_id>',
              type='http',
              auth='user',
              methods=['GET', 'OPTIONS'],
              csrf=False)
    def get_company_by_id(self, company_id, **kw):
        headers = self._get_cors_headers(methods='GET, OPTIONS')
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)
        try:
            company = request.env['res.company'].sudo().browse(company_id)
            if not company.exists():
                return self._make_json_response({'error': 'Company not found.'}, status=404, headers=headers)
            return self._make_json_response({'data': self._format_company_data(company)}, status=200, headers=headers)
        except Exception as e:
            _logger.error('Error in get_company_by_id: %s', e)
            return self._make_json_response({'error': 'Internal server error.'}, status=500, headers=headers)

class DepartmentAPI(http.Controller):
    """API Controller untuk mengakses data departemen."""
    
    _cors_origin = 'http://localhost:5173'

    def _get_cors_headers(self, methods='GET, OPTIONS'):
        """Helper untuk menghasilkan header CORS."""
        return {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': self._cors_origin,
            'Access-Control-Allow-Methods': methods,
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }

    def _format_department_data(self, department):
        """Helper untuk memformat data departemen."""
        if not department or not department.exists():
            return {}
            
        return {
            'id': department.id,
            'name': department.name,
            'complete_name': department.complete_name,
            'active': department.active,
            'company': {
                'id': department.company_id.id,
                'name': department.company_id.name
            } if department.company_id else None,
            'parent_department': {
                'id': department.parent_id.id,
                'name': department.parent_id.name
            } if department.parent_id else None,
            'manager': {
                'id': department.manager_id.id,
                'name': department.manager_id.name
            } if department.manager_id else None,
            'note': department.note or None,
            'total_employees': len(department.member_ids) if department.member_ids else 0
        }

    def _make_json_response(self, data, status=200, headers={}):
        """Helper untuk membuat response JSON."""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
        headers.update(security_headers)
        return Response(json.dumps(data), status=status, headers=headers)

    @http.route('/api/departments',
              type='http',
              auth='public',
              methods=['GET', 'OPTIONS'],
              csrf=False)
    def get_departments(self, **kw):
        """
        Endpoint untuk mendapatkan daftar departemen.
        Query parameters:
        - limit: jumlah maksimum data
        - offset: index awal
        - company: filter berdasarkan company (id atau nama)
        - name: filter berdasarkan nama departemen
        - active: filter berdasarkan status aktif
        """
        headers = self._get_cors_headers(methods='GET, OPTIONS')
        
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)

        try:
            domain = []
            
            # Filter berdasarkan nama
            if kw.get('name'):
                domain.append(('name', 'ilike', kw.get('name')))

            # Filter berdasarkan company
            if kw.get('company'):
                company_param = kw.get('company')
                try:
                    comp_id = int(company_param)
                    domain.append(('company_id', '=', comp_id))
                except ValueError:
                    domain.append(('company_id.name', 'ilike', company_param))

            # Filter berdasarkan status aktif
            if 'active' in kw:
                domain.append(('active', '=', kw.get('active').lower() == 'true'))

            # Paginasi
            try:
                limit = min(int(kw.get('limit', 50)), 100)
                offset = max(int(kw.get('offset', 0)), 0)
            except ValueError:
                return self._make_json_response(
                    {'error': 'Parameter limit dan offset harus berupa angka.'},
                    status=400, headers=headers
                )

            # Ambil data departemen
            Department = request.env['hr.department'].sudo()
            departments = Department.search(domain, limit=limit, offset=offset)
            
            # Format data
            data = [self._format_department_data(dept) for dept in departments]
            total_count = Department.search_count(domain)

            response_data = {
                'count': len(data),
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'data': data
            }
            
            return self._make_json_response(response_data, status=200, headers=headers)

        except Exception as e:
            _logger.error("Error in get_departments: %s", str(e))
            return self._make_json_response(
                {'error': 'Terjadi kesalahan internal server.'},
                status=500, headers=headers
            )

    @http.route('/api/departments/<int:department_id>',
              type='http',
              auth='public',
              methods=['GET', 'OPTIONS'],
              csrf=False)
    def get_department_by_id(self, department_id, **kw):
        """Endpoint untuk mendapatkan detail satu departemen."""
        headers = self._get_cors_headers(methods='GET, OPTIONS')
        
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)

        try:
            department = request.env['hr.department'].sudo().browse(department_id)
            if not department.exists():
                return self._make_json_response(
                    {'error': 'Departemen tidak ditemukan.'},
                    status=404, headers=headers
                )

            return self._make_json_response(
                {'data': self._format_department_data(department)},
                status=200, headers=headers
            )

        except Exception as e:
            _logger.error("Error in get_department_by_id: %s", str(e))
            return self._make_json_response(
                {'error': 'Terjadi kesalahan internal server.'},
                status=500, headers=headers
            )

class ProductAPI(http.Controller):
    """API Controller untuk mengakses data produk inventory."""
    
    _cors_origin = 'http://localhost:5173'

    def _get_cors_headers(self, methods='GET, OPTIONS'):
        """Helper untuk menghasilkan header CORS."""
        return {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': self._cors_origin,
            'Access-Control-Allow-Methods': methods,
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true',
        }

    def _format_product_data(self, product):
        """Helper untuk memformat data produk ke dict."""
        if not product or not product.exists():
            return {}
        # Build absolute image URL using Odoo's /web/image route. This keeps
        # payloads small by default and lets frontend fetch the binary when needed.
        host_url = request.httprequest.host_url.rstrip('/') if request and request.httprequest else ''
        image_url = None
        if host_url:
            # Use product.template model image_1920 field
            image_url = f"{host_url}/web/image?model=product.template&field=image_1920&id={product.id}&unique=1"

        return {
            'id': product.id,
            'name': product.name,
            'default_code': product.default_code,
            'barcode': product.barcode,
            'list_price': product.list_price,
            'standard_price': product.standard_price,
            'qty_available': product.qty_available,
            'virtual_available': product.virtual_available,
            'uom': product.uom_id.name if product.uom_id else None,
            'category': product.categ_id.name if product.categ_id else None,
            'company': product.company_id.name if getattr(product, 'company_id', None) else None,
            'type': product.type,
            'description': product.description or None,
            'weight': product.weight,
            'volume': product.volume,
            'active': product.active,
            'image_url': image_url,
            # NOTE: image (base64) is expensive; include only when requested via query param
            # The controller methods will optionally populate 'image' when include_image=true
            # to avoid sending large payloads by default.
            # 'image' key will not be present here by default.
        }

    def _make_json_response(self, data, status=200, headers={}):
        """Helper untuk membuat response JSON terstandardisasi."""
        return Response(
            json.dumps(data),
            status=status,
            headers=headers
        )
    
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

    # === ENDPOINT PRODUCTS ===
    
    @http.route('/api/products', 
              type='http', 
              auth='public',  # Ganti ke auth="user" untuk produksi
              methods=['GET', 'OPTIONS'], 
              csrf=False)
    def get_products(self, **kw):
        """
        Endpoint untuk mendapatkan semua produk.
        Optional query parameters:
        - limit: jumlah maksimum produk yang dikembalikan
        - offset: mulai dari index berapa
        - category: filter berdasarkan kategori
        - active: filter berdasarkan status aktif/tidak
        """
        headers = self._get_cors_headers(methods='GET, OPTIONS')
        
        # Handle pre-flight OPTIONS request
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)
            
        try:
            # Persiapkan domain pencarian
            domain = []
            
            # Filter berdasarkan kategori jika ada
            if kw.get('category'):
                domain.append(('categ_id.name', 'ilike', kw.get('category')))
            # Filter berdasarkan company (boleh id atau nama)
            if kw.get('company'):
                company_param = kw.get('company')
                # jika numeric, cocokkan berdasarkan id, jika tidak gunakan ilike pada nama
                try:
                    comp_id = int(company_param)
                    domain.append(('company_id', '=', comp_id))
                except Exception:
                    domain.append(('company_id.name', 'ilike', company_param))
                
            # Filter berdasarkan status aktif
            if 'active' in kw:
                domain.append(('active', '=', kw.get('active').lower() == 'true'))
                
            # Ambil parameter paginasi
            limit = int(kw.get('limit', 0))
            offset = int(kw.get('offset', 0))
            
            # Check if caller wants base64 image in responses (off by default)
            include_image = str(kw.get('include_image', 'false')).lower() == 'true'

            # Ambil data produk
            Product = request.env['product.template'].sudo()
            products = Product.search(domain, limit=limit, offset=offset)

            # Format data produk
            data = []
            for p in products:
                item = self._format_product_data(p)
                if include_image:
                    # product.image_1920 is base64 string in Odoo; might be large
                    try:
                        item['image'] = p.image_1920 or None
                    except Exception:
                        item['image'] = None
                data.append(item)
            
            # Hitung total produk untuk informasi paginasi
            total_count = Product.search_count(domain)
            
            response_data = {
                'count': len(data),
                'total': total_count,
                'offset': offset,
                'data': data
            }
            
            return self._make_json_response(response_data, status=200, headers=headers)
            
        except Exception as e:
            return self._make_json_response(
                {'error': str(e), 'message': 'Gagal mengambil data produk.'}, 
                status=500, headers=headers
            )

    @http.route('/api/products/<int:product_id>', 
              type='http', 
              auth='public',  # Ganti ke auth="user" untuk produksi
              methods=['GET', 'OPTIONS'], 
              csrf=False)
    def get_product_by_id(self, product_id, **kw):
        """
        Endpoint untuk mendapatkan detail satu produk berdasarkan ID.
        """
        headers = self._get_cors_headers(methods='GET, OPTIONS')

        # Handle pre-flight OPTIONS
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=headers)

        try:
            product = request.env['product.template'].sudo().browse(product_id)
            if not product.exists():
                return self._make_json_response(
                    {'error': 'Produk tidak ditemukan.'}, 
                    status=404, headers=headers
                )

            # include_image optional query param
            include_image = str(kw.get('include_image', 'false')).lower() == 'true'

            formatted_data = self._format_product_data(product)
            if include_image:
                try:
                    formatted_data['image'] = product.image_1920 or None
                except Exception:
                    formatted_data['image'] = None

            return self._make_json_response(
                {'data': formatted_data}, 
                status=200, headers=headers
            )

        except Exception as e:
            return self._make_json_response(
                {'error': str(e), 'message': 'Gagal mengambil detail produk.'}, 
                status=500, headers=headers
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
