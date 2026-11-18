import re
from datetime import timedelta

import pyotp
from cryptography.fernet import Fernet
from django.core import mail
from django.test import override_settings
from django.utils import timezone

from accounts.models import MfaBackupCode
from accounts.services.shared.account_rules import assign_role
from accounts.tests.base import AuthApiTestCase

RESET = "/api/auth/reset-password/"
NEW_PASSWORD = "a fresh strong secret"


@override_settings(MFA_ENCRYPTION_KEY=Fernet.generate_key().decode())
class ResetPasswordWithAuthenticatorTests(AuthApiTestCase):
    def set_up_account(self, role, email):
        user = self.verified_user(email=email)
        assign_role(user, role)
        return user

    def enrol_authenticator(self, email):
        self.authorize(self.sign_in(email=email).data["access_token"])
        enrolled = self.post("/api/auth/mfa/enrol/")
        totp = pyotp.TOTP(enrolled.data["secret"])
        confirmed = self.post("/api/auth/mfa/confirm/", {"code": totp.now()})
        self.client.credentials()
        return totp, confirmed.data["backup_codes"]

    def request_link(self, email):
        mail.outbox.clear()
        self.post("/api/auth/forgot-password/", {"email": email})
        return self.last_link_token()

    def reset(self, token, **extra):
        return self.post(RESET, {"token": token, "new_password": NEW_PASSWORD, **extra})

    def preview(self, token):
        return self.client.get(RESET, {"token": token})

    def next_code(self, totp, used_code):
        later = timezone.now() + timedelta(seconds=30)
        code = totp.at(later)
        return code if code != used_code else totp.at(later + timedelta(seconds=30))

    def test_a_tenant_resets_with_the_email_link_alone(self):
        self.set_up_account("TENANT", "tess@example.com")
        token = self.request_link("tess@example.com")

        self.assertEqual(self.preview(token).data, {"requires_code": False})
        response = self.reset(token)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.sign_in(email="tess@example.com", password=NEW_PASSWORD).status_code, 200
        )

    def test_a_reset_tells_the_owner_by_email_that_the_password_changed(self):
        self.set_up_account("TENANT", "tess@example.com")
        token = self.request_link("tess@example.com")
        mail.outbox.clear()

        self.reset(token)

        self.assertEqual([m.subject for m in mail.outbox], ["Your RentTrace password was changed"])

    def test_the_reset_email_links_to_the_web_app(self):
        self.set_up_account("TENANT", "tess@example.com")
        self.request_link("tess@example.com")

        link = re.search(r"https?://\S+reset-password\?token=[\w-]+", mail.outbox[-1].body)

        self.assertIsNotNone(link)
        self.assertTrue(link.group(0).startswith("http://localhost:3000/"))

    def test_an_admin_with_an_authenticator_needs_a_valid_code(self):
        self.set_up_account("ADMIN", "ada@example.com")
        totp, _ = self.enrol_authenticator("ada@example.com")
        token = self.request_link("ada@example.com")

        self.assertEqual(self.preview(token).data, {"requires_code": True})
        missing = self.reset(token)
        self.assertEqual(missing.status_code, 400)
        self.assertIn("code", missing.data)

        code = self.next_code(totp, None)
        with_code = self.reset(token, code=code)

        self.assertEqual(with_code.status_code, 200, with_code.data)
        self.assertEqual(
            self.sign_in(email="ada@example.com", password=NEW_PASSWORD).status_code, 200
        )

    def test_a_missing_code_does_not_use_the_link_up(self):
        self.set_up_account("ADMIN", "ada@example.com")
        totp, _ = self.enrol_authenticator("ada@example.com")
        token = self.request_link("ada@example.com")

        self.reset(token)

        self.assertEqual(self.preview(token).status_code, 200)

    def test_a_wrong_code_uses_the_link_up(self):
        self.set_up_account("ADMIN", "ada@example.com")
        totp, _ = self.enrol_authenticator("ada@example.com")
        token = self.request_link("ada@example.com")

        wrong = self.reset(token, code="000000")
        retry = self.reset(token, code=self.next_code(totp, None))

        self.assertEqual(wrong.status_code, 400)
        self.assertIn("code", wrong.data)
        self.assertEqual(retry.status_code, 400)
        self.assertIn("token", retry.data)
        self.assertEqual(self.preview(token).status_code, 400)
        self.assertEqual(
            self.sign_in(email="ada@example.com", password=NEW_PASSWORD).status_code, 401
        )

    def test_a_backup_code_works_once(self):
        self.set_up_account("ADMIN", "ada@example.com")
        _, backup_codes = self.enrol_authenticator("ada@example.com")
        token = self.request_link("ada@example.com")

        response = self.reset(token, code=backup_codes[0])

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(MfaBackupCode.objects.unused().count(), len(backup_codes) - 1)

    def test_a_weak_password_with_a_right_code_leaves_everything_unused(self):
        self.set_up_account("ADMIN", "ada@example.com")
        totp, _ = self.enrol_authenticator("ada@example.com")
        token = self.request_link("ada@example.com")
        code = self.next_code(totp, None)

        weak = self.post(RESET, {"token": token, "new_password": "short", "code": code})
        retry = self.reset(token, code=code)

        self.assertEqual(weak.status_code, 400)
        self.assertEqual(retry.status_code, 200, retry.data)

    def test_a_bad_or_used_link_is_refused_by_the_preview(self):
        self.set_up_account("TENANT", "tess@example.com")
        token = self.request_link("tess@example.com")
        self.reset(token)

        self.assertEqual(self.preview(token).status_code, 400)
        self.assertEqual(self.preview("not-a-real-token").status_code, 400)

    def test_an_admin_who_never_set_up_an_authenticator_resets_by_email_alone(self):
        self.set_up_account("ADMIN", "ada@example.com")
        token = self.request_link("ada@example.com")

        self.assertEqual(self.preview(token).data, {"requires_code": False})
        self.assertEqual(self.reset(token).status_code, 200)
