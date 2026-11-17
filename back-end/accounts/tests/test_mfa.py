from datetime import timedelta
from unittest import mock

import pyotp
from cryptography.fernet import Fernet
from django.test import override_settings
from django.utils import timezone

from accounts.models import AuthSession, MfaBackupCode, User
from accounts.security.mfa_permission import MfaCompleted
from accounts.services.shared.account_rules import assign_role
from accounts.tests.base import AuthApiTestCase

EMAIL = "admin@example.com"


@override_settings(MFA_ENCRYPTION_KEY=Fernet.generate_key().decode())
class MfaTests(AuthApiTestCase):
    def sign_in_as(self, role="ADMIN", email=EMAIL):
        user = self.verified_user(email=email)
        assign_role(user, role)
        response = self.sign_in(email=email)
        self.authorize(response.data["access_token"])
        return response

    def enrol(self):
        response = self.post("/api/auth/mfa/enrol/")
        return response, pyotp.TOTP(response.data["secret"])

    def enrol_and_confirm(self):
        _, totp = self.enrol()
        self.confirm_code = totp.now()
        confirmed = self.post("/api/auth/mfa/confirm/", {"code": self.confirm_code})
        return confirmed, totp

    def test_admin_sign_in_reports_that_enrolment_is_needed(self):
        response = self.sign_in_as()

        self.assertEqual(response.data["mfa_status"], "ENROL")
        self.assertEqual(self.client.get("/api/auth/me/").data["mfa_status"], "ENROL")

    def test_tenant_does_not_need_mfa(self):
        response = self.sign_in_as(role="TENANT", email="ann2@example.com")

        self.assertEqual(response.data["mfa_status"], "NOT_REQUIRED")

    def test_super_admin_does_not_need_mfa(self):
        user = self.verified_user(email="root@example.com")
        assign_role(user, "ADMIN")
        User.objects.filter(pk=user.pk).update(is_top_level_admin=True)

        response = self.sign_in(email="root@example.com")

        self.assertEqual(response.data["mfa_status"], "NOT_REQUIRED")

    def test_enrol_returns_secret_and_uri_without_caching(self):
        self.sign_in_as()

        response, _ = self.enrol()

        self.assertEqual(response.status_code, 200)
        self.assertIn("otpauth://totp/", response.data["provisioning_uri"])
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_enrol_again_before_confirming_keeps_the_same_secret(self):
        self.sign_in_as()

        first, _ = self.enrol()
        second, _ = self.enrol()

        self.assertEqual(first.data["secret"], second.data["secret"])

    def test_non_admin_cannot_enrol(self):
        self.sign_in_as(role="TENANT")

        self.assertEqual(self.post("/api/auth/mfa/enrol/").status_code, 403)

    def test_confirm_verifies_the_session_and_returns_backup_codes_once(self):
        self.sign_in_as()

        confirmed, _ = self.enrol_and_confirm()

        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(len(confirmed.data["backup_codes"]), 10)
        self.assertEqual(self.client.get("/api/auth/me/").data["mfa_status"], "VERIFIED")
        self.assertEqual(MfaBackupCode.objects.count(), 10)

    def test_enrol_after_confirming_is_refused(self):
        self.sign_in_as()
        self.enrol_and_confirm()

        self.assertEqual(self.post("/api/auth/mfa/enrol/").status_code, 409)

    def test_wrong_code_is_refused(self):
        self.sign_in_as()
        self.enrol()

        response = self.post("/api/auth/mfa/confirm/", {"code": "000000"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/api/auth/me/").data["mfa_status"], "ENROL")

    def test_new_session_must_verify_and_a_used_code_cannot_be_replayed(self):
        self.sign_in_as()
        _, totp = self.enrol_and_confirm()
        self.authorize(self.sign_in(email=EMAIL).data["access_token"])
        self.assertEqual(self.client.get("/api/auth/me/").data["mfa_status"], "VERIFY")

        replay = self.post("/api/auth/mfa/verify/", {"code": self.confirm_code})
        next_step = self.post(
            "/api/auth/mfa/verify/", {"code": totp.at(timezone.now() + timedelta(seconds=30))}
        )

        self.assertEqual(replay.status_code, 400)
        self.assertEqual(next_step.status_code, 200)
        self.assertEqual(self.client.get("/api/auth/me/").data["mfa_status"], "VERIFIED")

    def test_backup_code_works_once(self):
        self.sign_in_as()
        confirmed, _ = self.enrol_and_confirm()
        backup = confirmed.data["backup_codes"][0]
        self.authorize(self.sign_in(email=EMAIL).data["access_token"])

        first = self.post("/api/auth/mfa/verify/", {"code": backup})
        self.authorize(self.sign_in(email=EMAIL).data["access_token"])
        second = self.post("/api/auth/mfa/verify/", {"code": backup})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 400)

    def test_verify_before_enrolling_is_refused(self):
        self.sign_in_as()

        self.assertEqual(self.post("/api/auth/mfa/verify/", {"code": "123456"}).status_code, 400)

    def test_refresh_keeps_the_session_verified(self):
        signed_in = self.sign_in_as()
        self.enrol_and_confirm()

        refreshed = self.post(
            "/api/auth/refresh/", {"refresh_token": signed_in.data["refresh_token"]}
        )

        self.assertEqual(refreshed.data["mfa_status"], "VERIFIED")

    def test_permission_blocks_until_mfa_is_done(self):
        self.sign_in_as()
        session = AuthSession.objects.get()
        request = mock.Mock(auth=session)

        blocked = MfaCompleted().has_permission(request, None)
        self.enrol_and_confirm()
        session.refresh_from_db()
        allowed = MfaCompleted().has_permission(mock.Mock(auth=session), None)

        self.assertFalse(blocked)
        self.assertTrue(allowed)

    @override_settings(MFA_ENCRYPTION_KEY="")
    def test_missing_key_turns_mfa_off(self):
        self.sign_in_as()

        self.assertEqual(self.post("/api/auth/mfa/enrol/").status_code, 503)

    @override_settings(MFA_ENCRYPTION_KEY="not-a-fernet-key")
    def test_malformed_key_turns_mfa_off(self):
        self.sign_in_as()

        self.assertEqual(self.post("/api/auth/mfa/enrol/").status_code, 503)
