from django.core import mail

from accounts.models import User
from communications.tests.base import LANDLORD_URL, TENANT_URL, ContactRequestApiTestCase


class RespondToContactRequestTests(ContactRequestApiTestCase):
    def setUp(self):
        super().setUp()
        self.request = self.asked()

    def tenant_sees(self):
        self.as_user(self.tina)
        return self.client.get(f"{TENANT_URL}{self.request['id']}/").data

    def test_accepting_reveals_the_landlords_contact_to_the_tenant(self):
        sent_before = len(mail.outbox)

        response = self.answer(self.request, "accept")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "ACCEPTED")
        saved = self.stored(self.request)
        self.assertEqual((saved.decided_by, saved.updated_by), (self.lou, self.lou))
        self.assertIsNotNone(saved.decided_at)
        self.assertEqual(
            self.tenant_sees()["landlord"],
            {"name": "Lou Reed", "email": "lou@example.com", "phone_number": "0400 000 111"},
        )
        self.assertEqual(mail.outbox[-1].to, ["tina@example.com"])
        self.assertEqual(len(mail.outbox), sent_before + 1)
        self.assertNotIn("0400", mail.outbox[-1].body)

    def landlord_sees(self):
        self.as_user(self.lou)
        return self.client.get(f"{LANDLORD_URL}{self.request['id']}/").data

    def test_the_landlord_sees_the_tenants_contact_only_once_accepted(self):
        self.assertIsNone(self.landlord_sees()["tenant_contact"])

        self.answer(self.request, "accept")

        seen = self.landlord_sees()
        self.assertEqual(
            seen["tenant_contact"], {"email": "tina@example.com", "phone_number": None}
        )
        self.assertIn("Tina", str(seen["tenant"]))

    def test_the_tenants_phone_is_included_when_they_have_one(self):
        User.objects.filter(pk=self.tina.pk).update(phone_number="0411 222 333")
        self.answer(self.request, "accept")

        self.assertEqual(self.landlord_sees()["tenant_contact"]["phone_number"], "0411 222 333")

    def test_declining_or_revoking_keeps_the_tenants_contact_hidden(self):
        self.answer(self.request, "decline")
        self.assertIsNone(self.landlord_sees()["tenant_contact"])

        other = self.asked()
        self.answer(other, "accept")
        self.answer(other, "revoke")
        self.as_user(self.lou)
        revoked = self.client.get(f"{LANDLORD_URL}{other['id']}/").data
        self.assertIsNone(revoked["tenant_contact"])

    def test_the_landlord_list_carries_the_contact_for_accepted_requests_only(self):
        self.answer(self.request, "accept")
        pending = self.asked(self.make_user("sam@example.com", "TENANT", "Sam", "Fox"))

        self.as_user(self.lou)
        rows = {row["id"]: row for row in self.client.get(LANDLORD_URL).data["results"]}

        self.assertEqual(rows[self.request["id"]]["tenant_contact"]["email"], "tina@example.com")
        self.assertIsNone(rows[pending["id"]]["tenant_contact"])

    def test_declining_keeps_the_contact_hidden(self):
        self.assertEqual(self.answer(self.request, "decline").data["status"], "DECLINED")

        seen = self.tenant_sees()

        self.assertEqual((seen["status"], seen["landlord"]), ("DECLINED", None))

    def test_revoking_an_accepted_request_hides_the_contact_again(self):
        self.answer(self.request, "accept")
        sent = len(mail.outbox)

        revoked = self.answer(self.request, "revoke")

        self.assertEqual(revoked.data["status"], "REVOKED")
        self.assertIsNone(self.tenant_sees()["landlord"])
        self.assertEqual(len(mail.outbox), sent)

    def test_only_valid_moves_are_allowed(self):
        self.assertEqual(self.answer(self.request, "revoke").status_code, 400)
        self.answer(self.request, "accept")
        self.assertEqual(self.answer(self.request, "accept").status_code, 400)
        self.assertEqual(self.answer(self.request, "decline").status_code, 400)

    def test_another_landlord_cannot_see_or_answer_it(self):
        self.as_user(self.amy)

        self.assertEqual(self.client.get(f"{LANDLORD_URL}{self.request['id']}/").status_code, 404)
        self.assertEqual(self.answer(self.request, "accept", landlord=self.amy).status_code, 404)
        self.assertEqual(self.stored(self.request).status, "PENDING")

    def test_the_landlord_lists_only_their_own_requests_and_can_filter(self):
        other, _ = self.listing(self.amy, suburb="Elsewhere")
        self.ask(listing_id=other["id"])
        self.answer(self.request, "decline")

        self.as_user(self.lou)
        everything = self.client.get(LANDLORD_URL).data
        declined = self.client.get(LANDLORD_URL, {"status": "DECLINED"}).data
        pending = self.client.get(LANDLORD_URL, {"status": "PENDING"}).data

        self.assertEqual([r["id"] for r in everything["results"]], [self.request["id"]])
        self.assertEqual(declined["count"], 1)
        self.assertEqual(pending["count"], 0)
        self.assertEqual(everything["results"][0]["tenant"]["first_name"], "Tina")

    def test_tenants_and_admins_cannot_use_the_landlord_api(self):
        self.as_user(self.tina)
        self.assertEqual(self.client.get(LANDLORD_URL).status_code, 403)
        self.sign_in_as_admin()
        self.assertEqual(self.client.get(LANDLORD_URL).status_code, 403)
