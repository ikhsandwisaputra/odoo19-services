from odoo import models, fields, api

class PremiumFeature(models.Model):
    _name = 'premium.feature'
    _description = 'Premium Feature Placeholder'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

def action_learn_more(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/premium/learn_more',
            'target': 'new',
        }
def action_upgrade(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/premium/upgrade',
            'target': 'new',
        }