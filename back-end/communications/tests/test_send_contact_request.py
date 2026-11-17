from unittest import mock

from django.core import mail

from communications.models import ContactRequest
from communications.tests.base import TENANT_URL, ContactRequestApiTestCase
from properties.models import PropertyUnit


class SendContactRequestTests(ContactRequestApiTestCase):
    def test_a_tenant_asks_about_a_listing_and_the_landlord_is_emailed(self):
        sent_before = len(mail.outbox)

        response = self.ask(unit_id=self.unit["id"])

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["status"], "PENDING")
        self.assertEqual(response.data["unit"]["id"], self.unit["id"])
        self.assertEqual(response.data["listing"]["suburb"], "Carlton")
        self.assertIsNone(response.data["landlord"])
        saved = ContactRequest.objects.get()
        self.assertEqual((saved.tenant, saved.created_by), (self.tina, self.tina))
        self.assertEqual(len(mail.outbox), sent_before + 1)
        self.assertEqual(mail.outbox[-1].to, ["lou@example.com"])
        self.assertNotIn("0400", mail.outbox[-1].body)

    def test_the_unit_is_optional(self):
        self.assertIsNone(self.asked()["unit"])

    def test_an_unlisted_property_cannot_be_asked_about(self):
        hidden, _ = self.listing(status=None)

        response = self.ask(listing_id=hidden["id"])

        self.assertIn("listing_id", response.data)
        self.assertFalse(ContactRequest.objects.exists())

    def test_the_unit_must_be_an_available_public_unit_of_that_property(self):
        other, other_unit = self.listing(suburb="Fitzroy")
        taken = self.post(
            f"/api/landlord/properties/{self.made['id']}/units/",
            {"name": "Taken", "unit_type": "ROOM", "is_public": True},
        ).data
        PropertyUnit.objects.filter(pk=taken["id"]).update(occupancy_status="OCCUPIED")

        for unit_id in (other_unit["id"], taken["id"], 999999):
            self.assertIn("unit_id", self.ask(unit_id=unit_id).data)

    def test_one_open_request_per_property(self):
        self.asked()

        again = self.ask()

        self.assertIn("listing_id", again.data)
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_a_declined_tenant_may_ask_again(self):
        first = self.asked()
        self.answer(first, "decline")

        self.assertEqual(self.ask().status_code, 201)

    @mock.patch("communications.services.create_contact_request.MAX_PENDING_PER_TENANT", 2)
    def test_too_many_waiting_requests_are_refused(self):
        self.asked()
        second, _ = self.listing(suburb="Second")
        self.asked(listing_id=second["id"])
        third, _ = self.listing(suburb="Third")

        response = self.ask(listing_id=third["id"])

        self.assertEqual(response.status_code, 400)
        self.assertIn("too many", str(response.data))

    def test_the_message_is_required_and_limited(self):
        self.assertIn("message", self.ask(message="   ").data)
        self.assertIn("message", self.ask(message="x" * 1001).data)

    def test_only_tenants_can_ask(self):
        self.assertEqual(self.ask(self.lou).status_code, 403)
        self.sign_in_as_admin()
        self.assertEqual(self.post(TENANT_URL, {}).status_code, 403)

    def test_signing_in_is_required(self):
        self.client.credentials()
        self.assertEqual(self.post(TENANT_URL, {}).status_code, 401)
