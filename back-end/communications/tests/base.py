from accounts.models import User
from communications.models import ContactRequest
from listings.tests.test_public_listings_api import PublicListingsTestCase

TENANT_URL = "/api/tenant/contact-requests/"
LANDLORD_URL = "/api/landlord/contact-requests/"


class ContactRequestApiTestCase(PublicListingsTestCase):
    def setUp(self):
        super().setUp()
        User.objects.filter(pk=self.lou.pk).update(phone_number="0400 000 111")
        self.tina = self.make_user("tina@example.com", "TENANT", "Tina", "Ray")
        self.made, self.unit = self.listing(suburb="Carlton")

    def ask(self, user=None, **extra):
        self.as_user(user or self.tina)
        payload = {"listing_id": self.made["id"], "message": "Is it still free?", **extra}
        return self.post(TENANT_URL, payload)

    def asked(self, user=None, **extra):
        response = self.ask(user, **extra)
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def answer(self, request, action, landlord=None):
        self.as_user(landlord or self.lou)
        return self.post(f"{LANDLORD_URL}{request['id']}/{action}/")

    def stored(self, request):
        return ContactRequest.objects.get(pk=request["id"])
