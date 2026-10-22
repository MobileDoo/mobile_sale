from odoo import _, api, models


class MobileApi(models.AbstractModel):
    _inherit = 'mobile.api'

    @api.model
    def _mobile_features(self):
        return super()._mobile_features() + ['sale']

    @api.model
    def _mobile_record_services(self):
        return dict(super()._mobile_record_services(), sale='mobile.sale.service')

    @api.model
    def _mobile_access(self):
        access = super()._mobile_access()
        user = self.env.user
        if not self.env['sale.order'].has_access('read'):
            return access
        capabilities = {
            'view': user.has_group('sales_team.group_sale_salesman'),
            # Sales managers, and team leaders for their own team's quotations.
            'approve': self.env['mobile.sale.service']._mobile_is_approver(),
        }
        if any(capabilities.values()):
            access['sale'] = capabilities
            if capabilities['approve']:
                access.setdefault('dashboard', {})['view'] = True  # the overview shows what they can manage
        return access

    @api.model
    def _mobile_home_tiles(self):
        return super()._mobile_home_tiles() + [
            {'key': 'sale_to_approve', 'label': _('Confirm quotations'), 'feature': 'sale', 'capability': 'approve', 'sequence': 60},
            {'key': 'sale_mine', 'label': _('My quotations'), 'feature': 'sale', 'capability': 'view', 'sequence': 61},
        ]

    @api.model
    def _mobile_home_tabs(self):
        return super()._mobile_home_tabs() + [
            {'key': 'quotations', 'label': _('Quotations'), 'feature': 'sale', 'capability': 'view', 'sequence': 60},
        ]
