from accounts.models import AccountAccessHistory
from users.tests.base import UsersApiTestCase

URL = "/api/auth/profile/"


class UpdateProfileTests(UsersApiTestCase):
    def patch(self, payload):
        return self.client.patch(URL, payload, format="json")

    def sign_in_as(self, email, role):
        user = self.make_user(email, role, "Ann", "Lee")
        self.sign_in_user(user)
        return user

    def test_a_tenant_edits_their_own_details(self):
        user = self.sign_in_as("tina@example.com", "TENANT")

        response = self.patch(
            {"first_name": "Tina", "last_name": "Cole", "phone_number": "+61 400 123 456"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Tina")
        self.assertEqual(response.data["phone_number"], "+61 400 123 456")
        user.refresh_from_db()
        self.assertEqual((user.last_name, user.updated_by, user.row_version), ("Cole", user, 2))

    def test_a_landlord_edits_their_own_details(self):
        self.sign_in_as("lou@example.com", "LANDLORD")

        response = self.patch({"first_name": "Louise"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["last_name"], "Lee")

    def test_an_admin_who_finished_two_step_verification_edits_their_details(self):
        self.sign_in_as_admin(email="boss@example.com")

        response = self.patch({"first_name": "Bo"})

        self.assertEqual(response.status_code, 200)

    def test_an_admin_still_enrolling_two_step_verification_cannot_edit(self):
        self.sign_in_as_admin(email="boss@example.com", mfa_done=False)

        self.assertEqual(self.patch({"first_name": "Bo"}).status_code, 403)

    def test_the_email_cannot_be_changed(self):
        user = self.sign_in_as("tina@example.com", "TENANT")

        response = self.patch({"email": "new@example.com", "first_name": "Tina"})

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.email, "tina@example.com")

    def test_a_blank_phone_number_clears_it(self):
        user = self.sign_in_as("tina@example.com", "TENANT")
        self.patch({"phone_number": "0400 123 456"})

        response = self.patch({"phone_number": ""})

        self.assertIsNone(response.data["phone_number"])
        user.refresh_from_db()
        self.assertIsNone(user.phone_number)

    def test_bad_input_is_rejected_per_field(self):
        self.sign_in_as("tina@example.com", "TENANT")

        response = self.patch({"first_name": "  ", "phone_number": "call me"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.data), {"first_name", "phone_number"})

    def test_a_change_is_recorded_and_an_unchanged_save_is_not(self):
        user = self.sign_in_as("tina@example.com", "TENANT")

        self.patch({"first_name": "Tina"})
        self.patch({"first_name": "Tina"})

        history = AccountAccessHistory.objects.filter(user=user, action="UPDATED_OWN_PROFILE")
        self.assertEqual(history.count(), 1)
        entry = history.get()
        self.assertEqual(entry.created_by, user)
        self.assertEqual(
            (entry.before_values, entry.after_values),
            ({"first_name": "Ann"}, {"first_name": "Tina"}),
        )

    def test_someone_who_has_not_finished_onboarding_cannot_edit(self):
        user = self.verified_user("new@example.com")
        user.role_bridges.update(is_active=False)
        self.sign_in_user(user)

        self.assertEqual(self.patch({"first_name": "Nia"}).status_code, 403)

    def test_signing_in_is_required(self):
        self.assertEqual(self.patch({"first_name": "Nia"}).status_code, 401)

    def test_me_reports_the_account_summary(self):
        self.sign_in_as("tina@example.com", "TENANT")

        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.data["role_names"], ["Tenant"])
        self.assertIn("created_at", response.data)
        self.assertIn("last_login_at", response.data)
