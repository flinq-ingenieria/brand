# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_analytic_distribution_arguments(self):
        """
        Add the brand inside the arguments
        """
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "product_categ_id": self.product_id.categ_id.id,
            "partner_id": self.order_id.partner_id.id,
            "partner_category_id": self.order_id.partner_id.category_id.ids,
            "company_id": self.company_id.id,
            "brand_id": self.order_id.brand_id.id,
        }

    @staticmethod
    def _merge_analytic_distribution(base_distribution, extra_distribution):
        result = dict(base_distribution or {})
        for account_id, percentage in (extra_distribution or {}).items():
            result[account_id] = result.get(account_id, 0.0) + percentage
        return result

    @api.depends("order_id.partner_id", "product_id", "order_id.brand_id")
    def _compute_analytic_distribution(self):
        distribution_model = self.env["account.analytic.distribution.model"]
        for line in self:
            if line.display_type:
                continue
            arguments = line._get_analytic_distribution_arguments()
            base_arguments = dict(arguments)
            base_arguments.pop("brand_id", None)
            base_distribution = dict(
                distribution_model._get_distribution(base_arguments) or {}
            )
            line.analytic_distribution = base_distribution
            brand_distribution = distribution_model._get_brand_distribution(arguments)
            if brand_distribution:
                line.analytic_distribution = self._merge_analytic_distribution(
                    base_distribution, brand_distribution
                )
