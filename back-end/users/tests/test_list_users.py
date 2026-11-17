from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from accounts.models import User
from users.tests.base import UsersApiTestCase


class ListUsersTests(UsersApiTestCase):
    def setUp(self):
        super().setUp()
        self.sign_in_as_admin(super_admin=True)

    def get(self, **params):
        return self.client.get("/api/users/", params)

    def test_returns_a_page_envelope_newest_first(self):
        self.make_user("one@example.com")
        newest = self.make_user("two@example.com")

        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.data), {"count", "page", "page_size", "total_pages", "results"}
        )
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["results"][0]["id"], newest.pk)
        self.assertEqual(response.data["results"][0]["roles"], ["TENANT"])
        self.assertNotIn("password", str(response.data))

    def test_pages_split_the_results_and_a_high_page_gives_the_last_one(self):
        for index in range(4):
            self.make_user(f"user{index}@example.com")

        first = self.get(page_size=2)
        beyond = self.get(page_size=2, page=99)

        self.assertEqual((len(first.data["results"]), first.data["total_pages"]), (2, 3))
        self.assertEqual(beyond.data["page"], 3)
        self.assertEqual(len(beyond.data["results"]), 1)

    def test_page_size_above_the_cap_is_refused(self):
        self.assertEqual(self.get(page_size=500).status_code, 400)

    def test_search_finds_by_name_and_email(self):
        self.make_user("zoe@example.com", first_name="Zoe", last_name="Quinn")
        self.make_user("bob@example.com", first_name="Bob", last_name="Stone")

        by_name = self.get(q="zoe quinn")
        by_email = self.get(q="bob@")

        self.assertEqual([u["email"] for u in by_name.data["results"]], ["zoe@example.com"])
        self.assertEqual([u["email"] for u in by_email.data["results"]], ["bob@example.com"])

    def test_filters_by_role_and_status(self):
        self.make_user("landlord@example.com", role="LANDLORD")
        suspended = self.make_user("sleepy@example.com")
        User.objects.filter(pk=suspended.pk).update(account_status="SUSPENDED")

        landlords = self.get(role="LANDLORD")
        suspended_users = self.get(status="SUSPENDED")

        self.assertEqual([u["email"] for u in landlords.data["results"]], ["landlord@example.com"])
        self.assertEqual([u["id"] for u in suspended_users.data["results"]], [suspended.pk])

    def test_soft_deleted_users_are_left_out(self):
        gone = self.make_user("gone@example.com")
        User.objects.filter(pk=gone.pk).update(deleted_at=timezone.now())

        emails = [u["email"] for u in self.get().data["results"]]

        self.assertNotIn("gone@example.com", emails)

    def test_query_count_does_not_grow_with_the_number_of_users(self):
        self.make_user("first@example.com")
        with CaptureQueriesContext(connection) as few:
            self.get(page_size=100)
        for index in range(5):
            self.make_user(f"user{index}@example.com")

        with CaptureQueriesContext(connection) as many:
            self.get(page_size=100)

        self.assertEqual(len(many), len(few))
