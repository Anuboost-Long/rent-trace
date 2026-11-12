import re
from datetime import date

from django.core import mail

from properties.models import PropertyUnit
from properties.tests.test_landlord_properties_api import LandlordApiTestCase
from tenancies.models import Tenancy, TenancyParty

LANDLORD_URL = "/api/landlord/tenancies/"
ADMIN_URL = "/api/tenancies/"
TENANT_URL = "/api/tenant/invitations/"


class TenancyApiTestCase(LandlordApiTestCase):
    def setUp(self):
        super().setUp()
        self.property = self.new_property(self.lou)
        self.unit = PropertyUnit.objects.create(
            property_id=self.property["id"], name="Flat 1", unit_type="APARTMENT"
        )
        self.tina = self.make_user("tina@example.com", "TENANT", "Tina", "Ray")

    def new_tenancy(self, landlord=None, **extra):
        self.as_user(landlord or self.lou)
        payload = {"property_unit_id": self.unit.pk, "start_date": "2026-12-01", **extra}
        response = self.post(LANDLORD_URL, payload)
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def invite(self, tenancy, email="tina@example.com", **extra):
        self.as_user(self.lou)
        return self.post(f"{LANDLORD_URL}{tenancy['id']}/invitations/", {"email": email, **extra})

    def invitation_token(self):
        return re.search(r"token=([\w-]+)", mail.outbox[-1].body).group(1)

    def add_tenant(self, tenancy_id, user, is_primary=False):
        return TenancyParty.objects.create(
            tenancy_id=tenancy_id, tenant=user, is_primary=is_primary, joined_at=date(2026, 12, 1)
        )

    def tenancy_row(self, tenancy):
        return Tenancy.objects.get(pk=tenancy["id"])
