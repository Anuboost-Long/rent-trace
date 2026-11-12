from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from accounts.models import User
from notifications.models import Notification
from tenancies.models import Tenancy, TenancyInvitation, TenancyParty
from tenancies.tests.base import ADMIN_URL, TENANT_URL, HousemateApiTestCase


class HousemateDecisionTests(HousemateApiTestCase):
    def kinds_for(self, person):
        return [row.kind for row in Notification.objects.filter(recipient=person).order_by("id")]

    def test_the_invitee_says_yes_first_then_the_landlord_and_the_person_joins(self):
        request = self.asked()

        accepted = self.accept(request)

        self.assertEqual(accepted.status_code, 200, accepted.data)
        self.assertEqual(
            (accepted.data["joined"], accepted.data["waiting_on"]), (False, ["LANDLORD"])
        )
        self.assertFalse(self.is_tenant(self.sam))

        approved = self.decide("approve", request)

        self.assertEqual(approved.status_code, 200, approved.data)
        self.assertEqual(approved.data["status"], "ACCEPTED")
        self.assertTrue(self.is_tenant(self.sam))
        self.assertEqual(TenancyParty.objects.get(tenant=self.sam).joined_at, timezone.now().date())

    def test_the_landlord_says_yes_first_then_the_invitee_and_the_person_joins(self):
        request = self.asked()

        approved = self.decide("approve", request)

        self.assertEqual(
            (approved.data["status"], approved.data["waiting_on"]), ("PENDING", ["INVITEE"])
        )
        self.assertFalse(self.is_tenant(self.sam))

        accepted = self.accept(request)

        self.assertEqual((accepted.status_code, accepted.data["joined"]), (200, True))
        self.assertTrue(self.is_tenant(self.sam))

    def test_joining_tells_the_tenant_who_asked_and_the_owners(self):
        request = self.asked()
        self.decide("approve", request)
        self.accept(request)

        self.assertIn("TENANCY_INVITATION_ACCEPTED", self.kinds_for(self.tina))
        self.assertIn("TENANCY_INVITATION_ACCEPTED", self.kinds_for(self.lou))

    def test_the_landlord_is_not_told_about_their_own_approval_joining_someone(self):
        request = self.asked()
        self.accept(request)
        before = self.kinds_for(self.lou)

        self.decide("approve", request)

        self.assertEqual(self.kinds_for(self.lou), before)
        self.assertEqual(self.kinds_for(self.tina)[-1], "TENANCY_INVITATION_ACCEPTED")

    def test_approving_tells_the_asker_and_the_invitee(self):
        request = self.asked()

        self.decide("approve", request)

        self.assertEqual(self.kinds_for(self.tina), ["TENANCY_HOUSEMATE_APPROVED"])
        self.assertIn("TENANCY_HOUSEMATE_APPROVED", self.kinds_for(self.sam))

    def test_declining_ends_it_and_the_person_can_no_longer_accept(self):
        request = self.asked()

        declined = self.decide("decline", request)

        self.assertEqual((declined.status_code, declined.data["status"]), (200, "DECLINED"))
        saved = TenancyInvitation.objects.get(pk=request["id"])
        self.assertEqual(
            (saved.landlord_decision, saved.landlord_decided_by), ("DECLINED", self.lou)
        )
        self.assertIsNotNone(saved.revoked_at)
        self.assertEqual(self.accept(request).status_code, 400)
        self.assertFalse(self.is_tenant(self.sam))
        self.assertEqual(self.kinds_for(self.tina), ["TENANCY_HOUSEMATE_DECLINED"])
        self.assertIn("TENANCY_HOUSEMATE_DECLINED", self.kinds_for(self.sam))

    def test_declining_after_the_invitee_accepted_still_stops_them_joining(self):
        request = self.asked()
        self.accept(request)

        self.assertEqual(self.decide("decline", request).status_code, 200)

        self.assertFalse(self.is_tenant(self.sam))

    def test_only_a_tenant_request_waiting_for_a_decision_can_be_decided(self):
        request = self.asked()
        self.decide("approve", request)
        self.assertEqual(self.decide("approve", request).status_code, 404)
        self.assertEqual(self.decide("decline", request).status_code, 404)
        self.as_user(self.lou)
        landlords = self.post(
            f"/api/landlord/tenancies/{self.tenancy['id']}/invitations/",
            {"email": "new@example.com"},
        ).data
        self.assertEqual(self.decide("approve", landlords).status_code, 404)

    def test_another_landlord_tenants_and_signed_out_visitors_cannot_decide(self):
        request = self.asked()

        self.assertEqual(self.decide("approve", request, user=self.amy).status_code, 404)
        self.assertEqual(self.decide("approve", request, user=self.tina).status_code, 403)
        self.client.credentials()
        self.assertEqual(
            self.post(
                f"/api/landlord/tenancies/{self.tenancy['id']}/invitations/{request['id']}/approve/"
            ).status_code,
            401,
        )
        self.assertIsNone(TenancyInvitation.objects.get().landlord_decision)

    def test_an_admin_can_decide_on_any_tenancy(self):
        request = self.asked()
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")

        approved = self.post(
            f"{ADMIN_URL}{self.tenancy['id']}/invitations/{request['id']}/approve/"
        )

        self.assertEqual(approved.status_code, 200, approved.data)

    def test_only_the_tenant_who_asked_can_withdraw_and_then_nobody_can_accept(self):
        self.add_tenant(self.tenancy["id"], self.zed)
        request = self.asked()

        self.assertEqual(self.withdraw(request, user=self.zed).status_code, 404)
        self.assertEqual(self.withdraw(request).status_code, 200)

        self.assertEqual(self.accept(request).status_code, 400)

    def test_an_expired_request_cannot_be_approved_or_accepted(self):
        request = self.asked()
        TenancyInvitation.objects.update(
            created_at=timezone.now() - timedelta(days=9),
            expires_at=timezone.now() - timedelta(days=2),
        )

        self.assertEqual(self.decide("approve", request).status_code, 404)
        self.assertEqual(self.accept(request).status_code, 400)

    def test_an_account_that_went_bad_between_the_two_yeses_cannot_join(self):
        request = self.asked()
        self.accept(request)
        User.objects.filter(pk=self.sam.pk).update(account_status="SUSPENDED")

        response = self.decide("approve", request)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.is_tenant(self.sam))
        self.assertIsNone(TenancyInvitation.objects.get().landlord_decision)

    def test_an_ended_tenancy_refuses_the_second_yes(self):
        request = self.asked()
        self.accept(request)
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(status="ENDED")

        self.assertEqual(self.decide("approve", request).status_code, 400)
        self.assertFalse(self.is_tenant(self.sam))

    def test_someone_who_is_already_a_tenant_cannot_join_twice(self):
        request = self.asked()
        self.accept(request)
        self.add_tenant(self.tenancy["id"], self.sam)

        self.assertEqual(self.decide("approve", request).status_code, 400)

    def test_accepting_twice_is_harmless_and_a_wrong_account_is_refused(self):
        request = self.asked()
        self.accept(request)

        again = self.accept(request)
        stranger = self.accept(request, user=self.zed)

        self.assertEqual((again.status_code, again.data["waiting_on"]), (200, ["LANDLORD"]))
        self.assertEqual(stranger.status_code, 400)

    def test_accepting_by_the_emailed_token_works_too(self):
        from django.core import mail

        request = self.asked()
        body = next(m.body for m in reversed(mail.outbox) if m.to == ["sam@example.com"])
        token = body.split("token=")[1].split()[0]
        self.as_user(self.sam)

        response = self.post(f"{TENANT_URL}accept/", {"token": token})

        self.assertEqual((response.status_code, response.data["joined"]), (200, False))
        self.assertEqual(self.decide("approve", request).status_code, 200)
        self.assertTrue(self.is_tenant(self.sam))

    def test_the_landlord_cannot_resend_a_request_the_invitee_already_accepted(self):
        request = self.asked()
        resend_url = (
            f"/api/landlord/tenancies/{self.tenancy['id']}/invitations/{request['id']}/resend/"
        )
        self.as_user(self.lou)
        self.assertEqual(self.post(resend_url).status_code, 200)
        self.accept(request)

        self.as_user(self.lou)
        self.assertEqual(self.post(resend_url).status_code, 400)

    def test_the_invitee_sees_it_waiting_for_the_landlord_in_their_list(self):
        request = self.asked()
        self.accept(request)

        self.as_user(self.sam)
        rows = self.client.get(TENANT_URL).data

        self.assertEqual(
            [(row["id"], row["waiting_on"], row["requested_by_tenant"]) for row in rows],
            [(request["id"], ["LANDLORD"], True)],
        )

    def test_the_database_refuses_a_join_without_the_landlords_yes(self):
        request = self.asked()

        with self.assertRaises(IntegrityError), transaction.atomic():
            TenancyInvitation.objects.filter(pk=request["id"]).update(
                accepted_at=timezone.now(), accepted_by=self.sam, invitee_accepted_at=timezone.now()
            )
