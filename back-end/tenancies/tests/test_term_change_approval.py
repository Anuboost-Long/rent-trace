from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

from accounts.models import User
from notifications.models import Notification
from tenancies.models import Tenancy, TenancyParty, TenancyTermChange
from tenancies.tests.base import ADMIN_URL, LANDLORD_URL, TenancyApiTestCase

TENANT_TENANCIES = "/api/tenant/tenancies/"


class TermChangeApprovalTests(TenancyApiTestCase):
    """Tina lives in the tenancy and pays $450 a week with a $1,800 bond."""

    def setUp(self):
        super().setUp()
        self.tenancy = self.new_tenancy()
        self.edit({"rent_amount": "450", "rent_frequency": "WEEKLY", "bond_amount": "1800"})
        self.add_tenant(self.tenancy["id"], self.tina)
        self.sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")
        self._signed_in = None

    def acting_as(self, user):
        if self._signed_in != user.pk:
            self.as_user(user)
            self._signed_in = user.pk

    def edit(self, changes, url=LANDLORD_URL, user=None):
        self.as_user(user or self.lou)
        self._signed_in = None
        return self.client.patch(f"{url}{self.tenancy['id']}/", changes, format="json")

    def respond(self, action, change, user=None, tenancy=None):
        self.acting_as(user or self.tina)
        tenancy_id = (tenancy or self.tenancy)["id"]
        return self.post(f"{TENANT_TENANCIES}{tenancy_id}/changes/{change.pk}/{action}/")

    def row(self):
        return Tenancy.objects.get(pk=self.tenancy["id"])

    def open_change(self):
        return TenancyTermChange.objects.get(tenancy_id=self.tenancy["id"], status="PENDING")

    def propose(self, **changes):
        body = {"rent_amount": "500", "rent_frequency": "WEEKLY", **changes}
        response = self.edit(body)
        self.assertEqual(response.status_code, 200, response.data)
        return self.open_change()

    def kinds_for(self, person):
        return [row.kind for row in Notification.objects.filter(recipient=person).order_by("id")]

    # What needs approval

    def test_a_rent_rise_waits_for_the_tenants_and_the_rent_stays_as_it_was(self):
        response = self.edit({"rent_amount": "500", "rent_frequency": "WEEKLY"})

        self.assertEqual(self.row().rent_amount, Decimal("450.00"))
        pending = response.data["pending_change"]
        self.assertEqual(pending["status"], "PENDING")
        self.assertEqual(pending["before"]["rent_amount"], "450.00")
        self.assertEqual(pending["after"]["rent_amount"], "500.00")
        self.assertEqual(pending["approvals"], [{"name": "Tina Ray", "decision": None}])
        self.assertEqual(response.data["rent_amount"], "450.00")

    def test_a_bond_rise_waits_too(self):
        self.edit({"bond_amount": "2000"})

        self.assertEqual(self.row().bond_amount, Decimal("1800.00"))
        self.assertEqual(self.open_change().bond_amount, Decimal("2000.00"))

    def test_a_fall_or_an_equal_change_applies_at_once(self):
        lower = self.edit({"rent_amount": "400", "rent_frequency": "WEEKLY", "bond_amount": "1500"})

        self.assertEqual(lower.status_code, 200)
        self.assertIsNone(lower.data["pending_change"])
        self.assertEqual(
            (self.row().rent_amount, self.row().bond_amount),
            (Decimal("400.00"), Decimal("1500.00")),
        )
        self.assertFalse(TenancyTermChange.objects.pending().exists())

    def test_moving_the_same_money_to_another_frequency_is_judged_exactly(self):
        # $1,950 a month is exactly $450 a week over a year, so it is not a rise.
        same = self.edit({"rent_amount": "1950", "rent_frequency": "MONTHLY"})
        self.assertIsNone(same.data["pending_change"])
        self.assertEqual(self.row().rent_frequency, "MONTHLY")

        dearer = self.edit({"rent_amount": "1951", "rent_frequency": "MONTHLY"})
        self.assertIsNotNone(dearer.data["pending_change"])

    def test_the_same_amount_paid_less_often_is_a_fall(self):
        response = self.edit({"rent_amount": "450", "rent_frequency": "FORTNIGHTLY"})

        self.assertIsNone(response.data["pending_change"])
        self.assertEqual(self.row().rent_frequency, "FORTNIGHTLY")

    def test_setting_a_rent_where_there_was_none_counts_as_a_rise(self):
        TenancyTermChange.objects.all().delete()
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(rent_amount=None, rent_frequency=None)

        response = self.edit({"rent_amount": "300", "rent_frequency": "WEEKLY"})

        self.assertIsNotNone(response.data["pending_change"])
        self.assertIsNone(self.row().rent_amount)

    def test_a_mixed_edit_is_held_as_one_whole_proposal(self):
        response = self.edit(
            {"rent_amount": "500", "rent_frequency": "WEEKLY", "bond_amount": "1500"}
        )

        self.assertEqual(
            (self.row().rent_amount, self.row().bond_amount),
            (Decimal("450.00"), Decimal("1800.00")),
        )
        change = self.open_change()
        self.assertEqual(
            (change.rent_amount, change.bond_amount), (Decimal("500.00"), Decimal("1500.00"))
        )
        self.assertIsNotNone(response.data["pending_change"])

    def test_other_fields_in_the_same_edit_apply_at_once(self):
        response = self.edit({"rent_amount": "500", "rent_frequency": "WEEKLY", "notes": "Painted"})

        self.assertEqual(self.row().notes, "Painted")
        self.assertEqual(self.row().rent_amount, Decimal("450.00"))
        self.assertIsNotNone(response.data["pending_change"])

    def test_a_tenancy_with_no_tenants_applies_a_rise_at_once(self):
        TenancyParty.objects.all().delete()

        response = self.edit({"rent_amount": "900", "rent_frequency": "WEEKLY"})

        self.assertIsNone(response.data["pending_change"])
        self.assertEqual(self.row().rent_amount, Decimal("900.00"))

    # Approving and declining

    def test_the_only_tenant_approving_applies_the_change(self):
        change = self.propose()

        response = self.respond("approve", change)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.row().rent_amount, Decimal("500.00"))
        change.refresh_from_db()
        self.assertEqual(change.status, "APPLIED")
        self.assertIsNone(response.data["pending_change"])
        self.assertEqual(self.kinds_for(self.lou)[-1], "TENANCY_TERMS_APPLIED")

    def test_every_current_tenant_has_to_approve(self):
        self.add_tenant(self.tenancy["id"], self.sam)
        change = self.propose()

        first = self.respond("approve", change, self.tina)

        self.assertEqual(self.row().rent_amount, Decimal("450.00"))
        pending = first.data["pending_change"]
        self.assertEqual(pending["my_decision"], "APPROVED")
        self.assertEqual(
            {a["name"]: a["decision"] for a in pending["approvals"]},
            {"Tina Ray (you)": "APPROVED", "Sam Fox": None},
        )
        self.respond("approve", change, self.sam)
        self.assertEqual(self.row().rent_amount, Decimal("500.00"))

    def test_one_decline_ends_it_and_nothing_changes(self):
        self.add_tenant(self.tenancy["id"], self.sam)
        change = self.propose()
        self.respond("approve", change, self.tina)

        declined = self.respond("decline", change, self.sam)

        self.assertEqual(declined.status_code, 200)
        self.assertEqual(self.row().rent_amount, Decimal("450.00"))
        change.refresh_from_db()
        self.assertEqual(change.status, "DECLINED")
        self.assertEqual(self.kinds_for(self.lou)[-1], "TENANCY_TERMS_DECLINED")
        self.assertEqual(self.respond("approve", change, self.tina).status_code, 400)

    def test_a_declined_change_shows_in_the_tenants_history(self):
        change = self.propose()
        self.respond("decline", change)

        detail = self.client.get(f"{TENANT_TENANCIES}{self.tenancy['id']}/").data

        self.assertEqual([c["status"] for c in detail["term_history"]], ["DECLINED", "APPLIED"])

    def test_a_withdrawn_change_shows_in_the_tenants_history(self):
        self.propose()
        self.as_user(self.lou)
        open_change = self.open_change()
        self.post(f"{LANDLORD_URL}{self.tenancy['id']}/changes/{open_change.pk}/withdraw/")

        self.acting_as(self.tina)
        detail = self.client.get(f"{TENANT_TENANCIES}{self.tenancy['id']}/").data

        self.assertEqual([c["status"] for c in detail["term_history"]], ["WITHDRAWN", "APPLIED"])

    def test_a_tenant_cannot_change_their_answer(self):
        self.add_tenant(self.tenancy["id"], self.sam)
        change = self.propose()
        self.respond("approve", change, self.tina)

        self.assertEqual(self.respond("approve", change, self.tina).status_code, 200)
        self.assertEqual(self.respond("decline", change, self.tina).status_code, 400)

    def test_a_tenant_who_joined_since_has_to_approve_too(self):
        change = self.propose()
        self.add_tenant(self.tenancy["id"], self.sam)

        self.respond("approve", change, self.tina)

        self.assertEqual(self.row().rent_amount, Decimal("450.00"))
        self.respond("approve", change, self.sam)
        self.assertEqual(self.row().rent_amount, Decimal("500.00"))

    def test_a_tenant_who_left_does_not_block_it(self):
        self.add_tenant(self.tenancy["id"], self.sam)
        change = self.propose()
        TenancyParty.objects.filter(tenant=self.sam).update(left_at=date(2026, 12, 10))
        self.respond("approve", change, self.tina)

        self.assertEqual(self.row().rent_amount, Decimal("500.00"))

    def test_a_stale_proposal_is_refused_after_a_new_one_replaces_it(self):
        old = self.propose()
        new = self.propose(rent_amount="520")

        refused = self.respond("approve", old)

        self.assertEqual(refused.status_code, 400)
        self.assertEqual(self.row().rent_amount, Decimal("450.00"))
        old.refresh_from_db()
        self.assertEqual(old.status, "SUPERSEDED")
        self.assertEqual(self.respond("approve", new).status_code, 200)
        self.assertEqual(self.row().rent_amount, Decimal("520.00"))

    def test_an_expired_proposal_cannot_be_approved_and_a_new_one_replaces_it(self):
        change = self.propose()
        TenancyTermChange.objects.filter(pk=change.pk).update(
            expires_at=timezone.now() - timedelta(days=1)
        )

        refused = self.respond("approve", change)
        self.assertEqual(refused.status_code, 400)
        self.assertIn("expired", str(refused.data))
        detail = self.client.get(f"{TENANT_TENANCIES}{self.tenancy['id']}/").data
        self.assertEqual(detail["pending_change"]["status"], "EXPIRED")

        again = self.propose(rent_amount="510")
        self.assertNotEqual(again.pk, change.pk)

    def test_a_fall_applied_at_once_replaces_the_open_proposal(self):
        change = self.propose()

        self.edit({"rent_amount": "400", "rent_frequency": "WEEKLY"})

        change.refresh_from_db()
        self.assertEqual(change.status, "SUPERSEDED")
        self.assertEqual(self.respond("approve", change).status_code, 400)
        self.assertEqual(self.row().rent_amount, Decimal("400.00"))

    def test_withdrawing_stops_it(self):
        change = self.propose()

        self.as_user(self.lou)
        withdrawn = self.post(f"{LANDLORD_URL}{self.tenancy['id']}/changes/{change.pk}/withdraw/")

        self.assertEqual(withdrawn.status_code, 200, withdrawn.data)
        self.assertIsNone(withdrawn.data["pending_change"])
        self.assertEqual(self.respond("approve", change).status_code, 400)
        self.assertEqual(self.row().rent_amount, Decimal("450.00"))

    def test_ending_or_cancelling_closes_the_open_proposal(self):
        change = self.propose()
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(
            status="ACTIVE", start_date=timezone.now().date() - timedelta(days=30)
        )

        self.as_user(self.lou)
        self.assertEqual(self.post(f"{LANDLORD_URL}{self.tenancy['id']}/end/").status_code, 200)

        change.refresh_from_db()
        self.assertEqual(change.status, "CLOSED")
        self.assertEqual(self.respond("approve", change).status_code, 404)

    def test_an_ended_tenancy_can_not_be_approved_into(self):
        change = self.propose()
        Tenancy.objects.filter(pk=self.tenancy["id"]).update(status="ENDED")

        self.assertEqual(self.respond("approve", change).status_code, 400)

    # Who is allowed

    def test_someone_elses_tenancy_and_other_roles_are_refused(self):
        change = self.propose()

        self.assertEqual(self.respond("approve", change, self.sam).status_code, 404)
        self.assertEqual(self.respond("approve", change, self.lou).status_code, 403)
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self._signed_in = None
        self.assertEqual(
            self.post(
                f"{TENANT_TENANCIES}{self.tenancy['id']}/changes/{change.pk}/approve/"
            ).status_code,
            403,
        )
        self.assertEqual(self.row().rent_amount, Decimal("450.00"))

    def test_another_landlord_cannot_withdraw_and_a_tenant_cannot_withdraw(self):
        change = self.propose()
        url = f"{LANDLORD_URL}{self.tenancy['id']}/changes/{change.pk}/withdraw/"

        self.as_user(self.amy)
        self.assertEqual(self.post(url).status_code, 404)
        self.as_user(self.tina)
        self.assertEqual(self.post(url).status_code, 403)
        self.assertEqual(self.open_change().pk, change.pk)

    def test_an_admin_can_propose_and_withdraw(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self._signed_in = None
        proposed = self.client.patch(
            f"{ADMIN_URL}{self.tenancy['id']}/", {"bond_amount": "2500"}, format="json"
        )
        change = self.open_change()
        withdrawn = self.post(f"{ADMIN_URL}{self.tenancy['id']}/changes/{change.pk}/withdraw/")

        self.assertEqual((proposed.status_code, withdrawn.status_code), (200, 200))

    # What gets recorded and told

    def test_the_tenants_are_told_without_any_amounts(self):
        self.propose()
        change = self.open_change()
        self.respond("approve", change)

        text = " ".join(row.title + row.body for row in Notification.objects.all())

        self.assertEqual(
            self.kinds_for(self.tina), ["TENANCY_TERMS_PROPOSED", "TENANCY_TERMS_CHANGED"]
        )
        self.assertNotRegex(text, r"\d{3}")
        self.assertNotIn("$", text)

    def test_every_money_change_leaves_a_history_row(self):
        self.edit({"bond_amount": "1500"})
        change = self.propose()
        self.respond("approve", change)

        history = list(
            TenancyTermChange.objects.filter(tenancy_id=self.tenancy["id"]).order_by("id")
        )
        statuses = [(c.status, c.requires_approval) for c in history]
        self.assertEqual(statuses[-2:], [("APPLIED", False), ("APPLIED", True)])
        self.assertEqual(history[-1].from_rent_amount, Decimal("450.00"))
        self.assertEqual(history[-1].rent_amount, Decimal("500.00"))

        self.as_user(self.lou)
        detail = self.client.get(f"{LANDLORD_URL}{self.tenancy['id']}/").data
        self.assertGreaterEqual(len(detail["term_history"]), 2)

    def test_the_tenant_sees_what_took_effect_and_never_a_stranger_account(self):
        self.respond("approve", self.propose())

        detail = self.client.get(f"{TENANT_TENANCIES}{self.tenancy['id']}/").data

        self.assertEqual(detail["term_history"][0]["after"]["rent_amount"], "500.00")
        self.assertNotIn("lou@example.com", str(detail))

    def test_a_tenant_whose_account_is_suspended_cannot_answer(self):
        change = self.propose()
        self.acting_as(self.tina)
        User.objects.filter(pk=self.tina.pk).update(account_status="SUSPENDED")

        response = self.post(f"{TENANT_TENANCIES}{self.tenancy['id']}/changes/{change.pk}/approve/")

        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(self.row().rent_amount, Decimal("450.00"))
