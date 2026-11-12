from properties.models import PropertyUnit
from tenancies.models import TenancyParty
from tenancies.tests.base import LANDLORD_URL, HousemateApiTestCase

TENANT_TENANCIES = "/api/tenant/tenancies/"


class UnitCapacityTests(HousemateApiTestCase):
    def limit(self, people):
        PropertyUnit.objects.filter(pk=self.unit.pk).update(max_occupants=people)

    def party_count(self):
        return TenancyParty.objects.filter(tenancy_id=self.tenancy["id"]).current().count()

    def test_a_tenant_can_ask_while_there_is_room(self):
        self.limit(2)

        self.assertEqual(self.ask().status_code, 201)

    def test_a_full_unit_refuses_a_tenant_request_and_a_landlord_invitation(self):
        self.limit(2)
        self.add_tenant(self.tenancy["id"], self.zed)

        tenant_request = self.ask()
        self.as_user(self.lou)
        landlord_invite = self.post(
            f"{LANDLORD_URL}{self.tenancy['id']}/invitations/", {"email": "sam@example.com"}
        )

        for response in (tenant_request, landlord_invite):
            self.assertEqual(response.status_code, 400)
            self.assertIn("full (up to 2 people)", str(response.data))
        self.assertEqual(TenancyParty.objects.filter(tenant=self.sam).count(), 0)

    def test_no_limit_means_no_cap(self):
        for number in range(4):
            self.add_tenant(
                self.tenancy["id"], self.make_user(f"p{number}@example.com", "TENANT", "P", "Q")
            )

        self.assertEqual(self.ask().status_code, 201)

    def test_two_people_cannot_both_join_the_last_place(self):
        self.limit(2)
        first = self.asked("sam@example.com")
        second = self.asked("zed@example.com")
        self.decide("approve", first)
        self.decide("approve", second)

        joined = self.accept(first, user=self.sam)
        blocked = self.accept(second, user=self.zed)

        self.assertEqual(joined.status_code, 200)
        self.assertEqual(blocked.status_code, 400)
        self.assertIn("full", str(blocked.data))
        self.assertEqual(self.party_count(), 2)
        self.assertFalse(self.is_tenant(self.zed))

    def test_the_landlord_cannot_approve_into_a_unit_that_filled_up(self):
        self.limit(2)
        request = self.asked()
        self.accept(request)
        self.add_tenant(self.tenancy["id"], self.zed)

        response = self.decide("approve", request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("full", str(response.data))
        self.assertEqual(self.party_count(), 2)
        self.assertFalse(self.is_tenant(self.sam))

    def test_lowering_the_limit_below_the_people_already_there_removes_nobody(self):
        self.add_tenant(self.tenancy["id"], self.zed)
        self.as_user(self.lou)
        url = f"/api/landlord/properties/{self.property['id']}/units/{self.unit.pk}/"

        lowered = self.client.patch(url, {"max_occupants": 1}, format="json")

        self.assertEqual(lowered.status_code, 200, lowered.data)
        self.assertEqual(self.party_count(), 2)
        self.assertEqual(self.ask().status_code, 400)

    def test_the_tenant_sees_the_limit_the_count_and_only_their_own_requests(self):
        self.limit(3)
        self.add_tenant(self.tenancy["id"], self.zed)
        made = self.asked()

        mine = self.client.get(f"{TENANT_TENANCIES}{self.tenancy['id']}/").data
        self.as_user(self.zed)
        theirs = self.client.get(f"{TENANT_TENANCIES}{self.tenancy['id']}/").data

        self.assertEqual((mine["max_occupants"], mine["people_count"]), (3, 2))
        self.assertEqual(
            [(r["id"], r["email"], r["waiting_on"]) for r in mine["housemate_requests"]],
            [(made["id"], "sam@example.com", ["LANDLORD", "INVITEE"])],
        )
        self.assertEqual(theirs["housemate_requests"], [])
        self.assertNotIn("sam@example.com", str(theirs))

    def test_the_landlord_sees_who_asked_what_is_pending_and_the_count(self):
        self.limit(4)
        self.asked()

        self.as_user(self.lou)
        detail = self.client.get(f"{LANDLORD_URL}{self.tenancy['id']}/").data

        (request,) = detail["invitations"]
        self.assertEqual((detail["max_occupants"], detail["people_count"]), (4, 1))
        self.assertEqual(
            (request["requested_by"], request["requested_by_tenant"], request["waiting_on"]),
            ("Tina Ray", True, ["LANDLORD", "INVITEE"]),
        )
