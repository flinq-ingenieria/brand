# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @staticmethod
    def _merge_analytic_distribution(base_distribution, extra_distribution):
        result = dict(base_distribution or {})
        for account_id, percentage in (extra_distribution or {}).items():
            result[account_id] = result.get(account_id, 0.0) + percentage
        return result

    @api.depends("account_id", "partner_id", "product_id", "move_id.brand_id")
    def _compute_analytic_distribution(self):
        res = super()._compute_analytic_distribution()
        distribution_model = self.env["account.analytic.distribution.model"]
        for line in self.filtered(
            lambda l: l.display_type == "product"
            or not l.move_id.is_invoice(include_receipts=True)
        ):
            arguments = {
                "product_id": line.product_id.id,
                "product_categ_id": line.product_id.categ_id.id,
                "partner_id": line.partner_id.id,
                "partner_category_id": line.partner_id.category_id.ids,
                "account_prefix": line.account_id.code,
                "company_id": line.company_id.id,
                "brand_id": line.move_id.brand_id.id,
            }
            base_arguments = dict(arguments)
            base_arguments.pop("brand_id", None)
            base_distribution = (
                distribution_model._get_distribution(base_arguments) or {}
            )
            line.analytic_distribution = base_distribution
            if line.move_id.brand_id:
                brand_distribution = distribution_model._get_brand_distribution(
                    arguments
                )
                if brand_distribution:
                    line.analytic_distribution = self._merge_analytic_distribution(
                        base_distribution, brand_distribution
                    )
        return res
