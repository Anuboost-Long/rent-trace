from datetime import timedelta

import pyotp
from cryptography.fernet import Fernet
from django.core import mail
from django.test import override_settings
from django.utils import timezone

from accounts.models import MfaBackupCode
from accounts.services.shared.account_rules import assign_role
from accounts.tests.base import PASSWORD, AuthApiTestCase

CHANGE = "/api/auth/change-password/"
NEW_PASSWORD = "a fresh strong secret"


@override_settings(MFA_ENCRYPTION_KEY=Fernet.generate_key().decode())
class ChangePasswordWithAuthenticatorTests(AuthApiTestCase):
    def sign_in_as(self, role, email):
        user = self.verified_user(email=email)
        assign_role(user, role)
        self.authorize(self.sign_in(email=email).data["access_token"])
        return user

    def enrol_authenticator(self):
        enrolled = self.post("/api/auth/mfa/enrol/")
        totp = pyotp.TOTP(enrolled.data["secret"])
        confirmed = self.post("/api/auth/mfa/confirm/", {"code": totp.now()})
        return totp, confirmed.data["backup_codes"]

    def change(self, **extra):
        return self.post(
            CHANGE, {"current_password": PASSWORD, "new_password": NEW_PASSWORD, **extra}
        )

    def fresh_code(self, totp):
        return totp.at(timezone.now() + timedelta(seconds=30))

    def test_a_tenant_changes_the_password_with_the_current_password_alone(self):
        self.sign_in_as("TENANT", "tess@example.com")
        mail.outbox.clear()

        response = self.change()

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(
            self.sign_in(email="tess@example.com", password=NEW_PASSWORD).status_code, 200
        )

    def test_everyone_is_told_by_email_when_the_password_changes(self):
        self.sign_in_as("TENANT", "tess@example.com")
        mail.outbox.clear()

        self.change()

        self.assertEqual([m.subject for m in mail.outbox], ["Your RentTrace password was changed"])
        self.assertEqual(mail.outbox[0].to, ["tess@example.com"])

    def test_the_current_password_is_still_checked(self):
        self.sign_in_as("TENANT", "tess@example.com")

        response = self.post(
            CHANGE, {"current_password": "not my password!!", "new_password": NEW_PASSWORD}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("current_password", response.data)

    def test_an_admin_with_an_authenticator_needs_a_code(self):
        self.sign_in_as("ADMIN", "ada@example.com")
        totp, _ = self.enrol_authenticator()

        missing = self.change()
        wrong = self.change(code="000000")
        right = self.change(code=self.fresh_code(totp))

        self.assertEqual((missing.status_code, wrong.status_code), (400, 400))
        self.assertIn("code", missing.data)
        self.assertIn("code", wrong.data)
        self.assertEqual(right.status_code, 200, right.data)
        self.assertEqual(
            self.sign_in(email="ada@example.com", password=NEW_PASSWORD).status_code, 200
        )

    def test_a_refused_change_sends_no_email_and_keeps_the_password(self):
        self.sign_in_as("ADMIN", "ada@example.com")
        self.enrol_authenticator()
        mail.outbox.clear()

        self.change(code="000000")

        self.assertEqual(mail.outbox, [])
        self.assertEqual(self.sign_in(email="ada@example.com").status_code, 200)

    def test_a_backup_code_works_once(self):
        self.sign_in_as("ADMIN", "ada@example.com")
        _, backup_codes = self.enrol_authenticator()

        response = self.change(code=backup_codes[0])

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(MfaBackupCode.objects.unused().count(), len(backup_codes) - 1)

    def test_a_weak_password_with_a_right_code_leaves_the_code_usable(self):
        self.sign_in_as("ADMIN", "ada@example.com")
        totp, _ = self.enrol_authenticator()
        code = self.fresh_code(totp)

        weak = self.post(
            CHANGE, {"current_password": PASSWORD, "new_password": "short", "code": code}
        )
        retry = self.change(code=code)

        self.assertEqual(weak.status_code, 400)
        self.assertEqual(retry.status_code, 200, retry.data)
