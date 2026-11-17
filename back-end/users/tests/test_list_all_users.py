from unittest import mock

from users.tests.base import UsersApiTestCase


class ListAllUsersTests(UsersApiTestCase):
    def setUp(self):
        super().setUp()
        self.sign_in_as_admin(super_admin=True)

    def test_returns_a_plain_list_of_options(self):
        self.make_user("one@example.com", role="LANDLORD")

        response = self.client.get("/api/users/all/", {"role": "LANDLORD"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(set(response.data[0]), {"id", "email", "first_name", "last_name", "roles"})

    def test_is_capped(self):
        for index in range(3):
            self.make_user(f"user{index}@example.com")

        with mock.patch("users.services.list_all_users.ALL_USERS_LIMIT", 2):
            response = self.client.get("/api/users/all/")

        self.assertEqual(len(response.data), 2)
