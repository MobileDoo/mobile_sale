"""Quotations on mobile: salespeople follow theirs, managers confirm them.

Odoo has no built-in quotation approval: confirming the quotation is the
manager's decision. "To approve" lists the open quotations of the teams the
user leads (all of them for sales managers). Customer approval modules (an
extra "to approve" state, approve/reject buttons...) override `_mobile_domain`;
their buttons appear from the form view automatically.
"""
from odoo import _, api, models

# E-mails, PDFs, deliveries and invoicing stay on the web client.
DESKTOP_ONLY_BUTTONS = {
    'object:action_quotation_send', 'object:action_preview_sale_order', 'object:print_quotation',
    'object:action_view_invoice', 'object:action_view_delivery',
}
OPEN_STATES = ('draft', 'sent')


class MobileSaleService(models.AbstractModel):
    _name = 'mobile.sale.service'
    _inherit = 'mobile.record.service'
    _description = 'Mobile Sales Service'

    _mobile_model = 'sale.order'
    _mobile_feature = 'sale'
    _mobile_create_capability = None
    _mobile_scope_capabilities = {'mine': 'view', 'to_approve': 'approve'}
    _mobile_core_field_names = [
        'partner_id', 'client_order_ref', 'date_order', 'validity_date', 'user_id', 'team_id', 'payment_term_id',
        'amount_untaxed', 'amount_tax', 'amount_total', 'currency_id', 'state',
    ]
    _mobile_list_field_names = ['name', 'partner_id', 'date_order', 'amount_total', 'currency_id', 'state', 'user_id']
    _mobile_line_field = 'order_line'
    _mobile_line_field_names = ['display_type', 'name', 'product_uom_qty', 'product_uom_id', 'price_unit', 'discount',
                                'price_subtotal']

    @api.model
    def _mobile_is_approver(self):
        user = self.env.user
        if user.has_group('sales_team.group_sale_manager'):
            return True
        return user.has_group('sales_team.group_sale_salesman') and bool(
            self.env['crm.team'].search_count([('user_id', '=', user.id)], limit=1))

    @api.model
    def _mobile_domain(self, scope, params):
        if scope == 'mine':
            return [('user_id', '=', self.env.uid)]
        if scope == 'to_approve':
            domain = [('state', 'in', OPEN_STATES)]
            if not self.env.user.has_group('sales_team.group_sale_manager'):
                domain.append(('team_id.user_id', '=', self.env.uid))
            return domain
        return super()._mobile_domain(scope, params)

    @api.model
    def _mobile_search_domain(self, query):
        return ['|', '|', ('name', 'ilike', query), ('partner_id', 'ilike', query), ('client_order_ref', 'ilike', query)]

    @api.model
    def _mobile_order(self, scope):
        return 'date_order desc, id desc'

    @api.model
    def _mobile_buttons(self, record, buttons):
        buttons = [b for b in super()._mobile_buttons(record, buttons) if b['key'] not in DESKTOP_ONLY_BUTTONS]
        # "Create invoice" opens the down-payment wizard: invoicing stays on the web client.
        invoice_action = self.env.ref('sale.action_view_sale_advance_payment_inv', raise_if_not_found=False)
        if invoice_action:
            buttons = [b for b in buttons if b['key'] != f'action:{invoice_action.id}']
        return buttons

    @api.model
    def _mobile_on_state_change(self, order, old_state, new_state):
        """Tell the salesperson someone else confirmed or cancelled their quotation."""
        user = order.user_id
        if not user or user == self.env.user or old_state not in OPEN_STATES or new_state not in ('sale', 'cancel'):
            return
        title, body = self.with_context(lang=user.lang)._mobile_push_text(order, new_state)
        self.env['mobile.push.message']._enqueue(user, title, body, {
            'type': 'sale', 'model': 'sale.order', 'res_id': order.id, 'state': new_state,
        })

    @api.model
    def _mobile_push_text(self, order, state):
        """Texts in `self.env.lang` (the recipient's language)."""
        order = order.with_context(lang=self.env.lang)
        amount = f'{order.amount_total:,.2f} {order.currency_id.name or ""}'.strip()
        body = f'{order.name} · {order.partner_id.display_name} · {amount}'
        if state == 'sale':
            return _('Quotation confirmed'), body
        return _('Quotation cancelled'), body
