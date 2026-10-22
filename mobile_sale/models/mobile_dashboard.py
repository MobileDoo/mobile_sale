from odoo import _, api, models


class MobileDashboardService(models.AbstractModel):
    _inherit = 'mobile.dashboard.service'

    @api.model
    def _card_defs(self):
        return super()._card_defs() + [
            {'key': 'sale_to_approve', 'section': 'approvals', 'feature': 'sale', 'capability': 'approve',
             'build': '_card_sale_to_approve'},
            {'key': 'sale_revenue_month', 'section': 'sales', 'feature': 'sale', 'capability': 'approve',
             'build': '_card_sale_revenue_month'},
            {'key': 'sale_revenue_today', 'section': 'sales', 'feature': 'sale', 'capability': 'approve',
             'build': '_card_sale_revenue_today'},
        ]

    @api.model
    def _card_sale_to_approve(self):
        service = self.env['mobile.sale.service']
        return self._count_card(service._mobile_model, service._mobile_scope_domain('to_approve', {}),
                                _('Quotations to confirm'), 'file-document-edit-outline', 'green',
                                tile='sale_to_approve', tone_if_any='warn')

    @api.model
    def _card_sale_revenue_month(self):
        return self._amount_card('sale.order', [('state', 'in', ('sale', 'done'))], 'date_order', 'amount_untaxed',
                                 _('Sales this month'), 'cash-multiple', 'green', 'month', trend_months=6)

    @api.model
    def _card_sale_revenue_today(self):
        return self._amount_card('sale.order', [('state', 'in', ('sale', 'done'))], 'date_order', 'amount_untaxed',
                                 _('Sales today'), 'cash-check', 'green', 'day')
