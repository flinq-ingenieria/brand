# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.analytic.models.analytic_distribution_model import (
    NonMatchingDistribution,
)


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    brand_id = fields.Many2one(
        "res.brand",
        ondelete="cascade",
        help="Select a brand for which the analytic distribution will be used"
        " (e.g. create new customer invoice or Sales order linked to this brand, "
        "it will automatically take this as an analytic account)",
    )

    @api.model
    def _get_brand_distribution(self, vals):
        brand_id = vals.get("brand_id")
        if not brand_id:
            return {}
        domain = [("brand_id", "=", brand_id)]
        for fname, value in vals.items():
            if fname == "brand_id":
                continue
            domain += self._create_domain(fname, value) or []
        result = {}
        best_score = 0
        fnames = set(self._get_fields_to_check())
        for record in self.search(domain):
            try:
                score = sum(record._check_score(key, vals.get(key)) for key in fnames)
            except NonMatchingDistribution:
                continue
            if score > best_score:
                result = record.analytic_distribution
                best_score = score
        return result

    @api.model
    def _get_distribution(self, vals):
        domain = [("brand_id", "=", False)]
        for fname, value in vals.items():
            if fname == "brand_id":
                continue
            domain += self._create_domain(fname, value) or []
        best_score = 0
        result = {}
        fnames = set(self._get_fields_to_check()) - {"brand_id"}
        for record in self.search(domain):
            try:
                score = sum(record._check_score(key, vals.get(key)) for key in fnames)
                if score > best_score:
                    result = record.analytic_distribution
                    best_score = score
            except NonMatchingDistribution:
                continue
        return result
