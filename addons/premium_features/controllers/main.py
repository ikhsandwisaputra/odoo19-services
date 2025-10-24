from odoo import http
from odoo.http import request

class PremiumFeatureController(http.Controller):
    
    @http.route('/premium/learn_more', type='http', auth='user', website=True)
    def learn_more(self, **kwargs):
        return request.render('premium_feature.learn_more_template', {})
    
    @http.route('/premium/upgrade', type='http', auth='user', website=True)
    def upgrade(self, **kwargs):
        return request.render('premium_feature.upgrade_template', {})
