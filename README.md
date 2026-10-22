# Mobile Sales

![Odoo 20.0](https://img.shields.io/badge/Odoo-20.0-714B67) ![License LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue) ![Version 20.0.1.0.0](https://img.shields.io/badge/version-20.0.1.0.0-informational)

> Quotations and their confirmation by sales managers in the MobileDoo app.

Odoo 20 addon of [MobileDoo](https://github.com/MobileDoo) (`mobile_sale`).

## Overview

Quotations in the MobileDoo app: salespeople follow their quotations and sales managers or team leaders confirm them. Odoo has no
built-in quotation approval, so confirmation (`action_confirm`) *is* the manager's decision; custom approval states and buttons
appear automatically.

## Features

- **My quotations** (the user's quotations and orders) and **Confirm quotations** (open quotations: every one for sales managers,
  the team's for team leaders).
- Quotation detail with order lines, and an **editable full form** (lines, images) through the core's generic form for fields the
  view allows to edit.
- Search by customer, reference and more.
- **Push** to the salesperson when someone else confirms or cancels their quotation.
- Management overview cards `sale_to_approve`, `sale_revenue_month` and `sale_revenue_today` (company currency, compared with the
  previous period).

## Requirements

| | |
|---|---|
| Odoo | 20.0 (Community or Enterprise) |
| Odoo modules | `sale` |
| MobileDoo addons | [`mobile_connector`](https://github.com/MobileDoo/mobile_connector/tree/20.0) (same branch) |
| Client | the [MobileDoo](https://github.com/MobileDoo) app for Android and iPhone |

This branch targets **Odoo 20** only; use the branch of your Odoo version.

## Installation

```bash
git clone --branch 20.0 https://github.com/MobileDoo/mobile_sale.git
git clone --branch 20.0 https://github.com/MobileDoo/mobile_connector.git
# add the cloned folders to addons_path in odoo.conf, then:
odoo -d <database> -i mobile_sale --stop-after-init
```

The addon is the `mobile_sale/` folder at the root of the repository, so the repository folder itself can go on `addons_path`.

`auto_install` is set: Odoo installs `mobile_sale` by itself as soon as all its dependencies are installed, so putting the folders on `addons_path` and updating the Apps list is enough.

To upgrade after pulling a newer version: `odoo -d <database> -u mobile_sale --stop-after-init`.

## How it works

| Piece | Technical detail |
|---|---|
| Record service | `sale` on `sale.order`: scope `mine` (capability `view`) and `to_approve` (`approve`) |
| Services | `mobile.sale.service` (`_mobile_is_approver`, `_mobile_domain`, `_mobile_search_domain`, `_mobile_buttons`, `_mobile_on_state_change`, `_mobile_push_text`) |
| Routes | Generic `/records/sale/*` and, for editing lines, `/form/line/*` |

### Capabilities

| Capability | Granted when |
|---|---|
| `view` | member of `sales_team.group_sale_salesman` |
| `approve` | member of `sales_team.group_sale_manager`, **or** a salesperson who leads at least one sales team (`crm.team.user_id`) |

## Security

No groups, ACLs or data are added. Each call runs as the signed-in user, so the sales team and record rules of `sale.order` decide
which quotations a user can read or confirm.

## Extending

Replace the "to approve" definition with `_mobile_domain('to_approve', params)` (for example to require a custom state), adjust
buttons with `_mobile_buttons(record, buttons)`, and add fields with `_mobile_extra_fields`.

```python
class MobileSaleService(models.AbstractModel):
    _inherit = 'mobile.sale.service'

    @api.model
    def _mobile_domain(self, scope, params):
        if scope == 'to_approve':
            return [('state', '=', 'x_pending_discount_approval')]
        return super()._mobile_domain(scope, params)
```

## Contributing

Issues and pull requests are welcome. Open pull requests against the branch of the Odoo version you are fixing (this one is `20.0`) and
keep the change inside the `mobile_sale/` folder.

These repositories are published from MobileDoo's development repository, which remains the source of truth. A merged pull request is
taken back there, and the branches of the other Odoo versions are updated by the maintainers, so a fix is usually welcome even if you can
only test it on one version. `README.md` and `LICENSE` are generated at each release; changes to them are not carried back.

## License

LGPL-3: see [LICENSE](LICENSE).
