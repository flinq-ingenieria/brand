# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _get_analytic_distribution_arguments(self):
        self.ensure_one()
        partner = self.contract_id.partner_id
        product = self.product_id
        return {
            "product_id": product.id,
            "product_categ_id": product.categ_id.id,
            "partner_id": partner.id,
            "partner_category_id": partner.category_id.ids,
            "company_id": self.company_id.id,
            "brand_id": self.contract_id.brand_id.id,
        }

    @staticmethod
    def _merge_analytic_distribution(base_distribution, extra_distribution):
        result = dict(base_distribution or {})
        for account_id, percentage in (extra_distribution or {}).items():
            result[account_id] = result.get(account_id, 0.0) + percentage
        return result

    @api.depends(
        "contract_id.brand_id",
        "contract_id.partner_id",
        "product_id",
    )
    def _compute_analytic_distribution(self):
        distribution_model = self.env["account.analytic.distribution.model"]
        for rec in self:
            if rec.display_type:
                continue
            arguments = rec._get_analytic_distribution_arguments()
            base_arguments = dict(arguments)
            base_arguments.pop("brand_id", None)
            base_distribution = dict(
                distribution_model._get_distribution(base_arguments) or {}
            )
            rec.analytic_distribution = base_distribution
            brand_distribution = distribution_model._get_brand_distribution(arguments)
            if brand_distribution:
                rec.analytic_distribution = self._merge_analytic_distribution(
                    base_distribution, brand_distribution
                )
