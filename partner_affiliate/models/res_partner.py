# Copyright 2012 Camptocamp SA - Yannick Vaucher
# Copyright 2018 brain-tec AG - Raul Martin
# Copyright 2021 Therp BV - <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Support affiliate relations beween partners."""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def check_if_parent_company(parent_type: str | None, vat: str | None):
    if parent_type == "parent_company" and not vat:
        raise ValidationError(_("Vat is mandatory to create a Parent Company"))


"""Add relation affiliate_ids."""


class ResPartner(models.Model):
    _inherit = "res.partner"

    child_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Contacts",
        domain=[
            ("active", "=", True),
            ("is_company", "=", False),
        ],
    )

    affiliate_ids = fields.One2many(
        "res.partner",
        "parent_id",
        string="Affiliates",
        domain=[
            ("active", "=", True),
            ("is_company", "=", True),
        ],
    )

    type = fields.Selection(
        selection_add=[
            ("affiliate", "Affiliate"),
            ("parent_company", "Parent Company"),
        ],
        required=True,
        default="contact",
        ondelete={
            "affiliate": "set default",
            "parent_company": "set default",
        },
        compute="_compute_type",
        store=True,
    )

    @api.depends("parent_id", "company_type")
    def _compute_type(self):
        for partner in self:
            partner.type = partner._get_company_type()

    def _get_company_type(self):
        self.ensure_one()
        if self.company_type == "person":
            partner_type = "contact"
            return partner_type
        else:
            if self.parent_id:
                partner_type = "affiliate"
                return partner_type
            elif self.vat and self.vat != "":
                partner_type = "parent_company"
                return partner_type
            else:
                partner_type = "other"
                return partner_type

    def _get_name(self):
        if self.type == "affiliate":
            parent_name = self.parent_id.name or ""
            city_name = self.city or ""
            return f"{parent_name} ({city_name})"
        return super()._get_name()

    @api.onchange("parent_id", "zip", "country_id", "name")
    def _onchange_parent_id_or_city(self):
        if self.parent_id:
            self.name = self.parent_id.name

    @api.depends("parent_id.name", "zip", "country_id", "name")
    def _compute_affiliate_name(self):
        for partner in self:
            if partner.type == "affiliate":
                partner.name = partner.parent_id.name

    def _fields_sync(self, values):
        """A company that will have a parent set, must be an affiliate,

        Setting a company to type affiliate, will automatically prevent
        overriding the address from the parent, because that is only done for
        contact partners.

        Clearing a parent_id from a company should reset its type to contact.

        You could argue that the same should be true for individuals.
        """
        desired_type = self._get_company_type()
        if self.type != desired_type:
            super().write({"type": desired_type})
        return super()._fields_sync(values)

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.parent_id:
            res.vat = None
        return res

    @api.onchange("parent_id", "company_type")
    def onchange_get_partner_ids_domain(self):
        if self.company_type == "person":
            domain = [("type", "in", ["affiliate", "parent_company"])]
        else:
            domain = [("type", "=", "parent_company")]
        return {"domain": {"parent_id": domain}}
