from unittest import mock

from django.core import mail
from django.utils import timezone

from accounts.models import AccountAccessHistory, AuthSession, MfaBackupCode, UserMfa
from users.tests.base import UsersApiTestCase

SEND = "accounts.integrations.emails.EmailMultiAlternatives.send"
REASON = {"reason": "Confirmed by phone that it is really Ada. Lost her phone."}


class ResetAuthenticatorTests(UsersApiTestCase):
    def reset(self, user_id, data=REASON):
        return self.post(f"/api/users/{user_id}/reset-authenticator/", data)

    def was_reset(self, user):
        return self.client.get(f"/api/users/{user.pk}/").data["authenticator_was_reset"]

    def sign_in_boss(self):
        return self.sign_in_as_admin(super_admin=True, email="boss@example.com")

    def admin_with_authenticator(self, email="ada@example.com"):
        ada = self.make_admin_user(email, "ADMIN")
        UserMfa.objects.create(
            user=ada, secret_encrypted="not-a-real-secret", confirmed_at=timezone.now()
        )
        MfaBackupCode.objects.bulk_create(
            MfaBackupCode(user=ada, code_hash=f"hash-{n}") for n in range(3)
        )
        self.sign_in(email=ada.email)
        return ada

    def test_a_super_admin_resets_the_authenticator_and_the_person_must_set_up_again(self):
        ada = self.admin_with_authenticator()
        self.sign_in_boss()
        mail.outbox.clear()

        response = self.reset(ada.pk)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(response.data["has_authenticator"])
        self.assertTrue(response.data["notice_sent"])
        self.assertFalse(UserMfa.objects.filter(user=ada).exists())
        self.assertFalse(MfaBackupCode.objects.filter(user=ada).exists())
        self.assertFalse(AuthSession.objects.filter(user=ada, revoked_at__isnull=True).exists())
        self.assertEqual([m.to for m in mail.outbox], [["ada@example.com"]])
        self.assertEqual(mail.outbox[0].subject, "Your RentTrace authenticator was reset")
        self.client.credentials()
        signed_in = self.sign_in(email="ada@example.com")
        self.assertEqual(signed_in.data["mfa_status"], "ENROL")

    def test_the_account_history_records_who_why_and_nothing_secret(self):
        ada = self.admin_with_authenticator()
        boss = self.sign_in_boss()

        self.reset(ada.pk)

        entry = AccountAccessHistory.objects.get(action="ADMIN_RESET_AUTHENTICATOR")
        self.assertEqual((entry.user, entry.created_by), (ada, boss))
        self.assertEqual(entry.reason, REASON["reason"])
        self.assertEqual(entry.before_values, {"authenticator": "SET_UP", "unused_backup_codes": 3})
        self.assertEqual(
            entry.after_values, {"authenticator": "NOT_SET_UP", "unused_backup_codes": 0}
        )
        self.assertNotIn("not-a-real-secret", str(entry.before_values))

    def test_the_detail_says_whether_an_authenticator_is_set_up(self):
        ada = self.admin_with_authenticator()
        tess = self.make_user("tess@example.com")
        self.sign_in_boss()

        self.assertTrue(self.client.get(f"/api/users/{ada.pk}/").data["has_authenticator"])
        self.assertFalse(self.client.get(f"/api/users/{tess.pk}/").data["has_authenticator"])

    def test_a_reason_is_required(self):
        ada = self.admin_with_authenticator()
        self.sign_in_boss()

        self.assertEqual(self.reset(ada.pk, {}).status_code, 400)
        self.assertTrue(UserMfa.objects.filter(user=ada).exists())

    def test_someone_with_no_authenticator_is_refused(self):
        tess = self.make_user("tess@example.com")
        self.sign_in_boss()

        self.assertEqual(self.reset(tess.pk).status_code, 400)

    def test_you_cannot_reset_your_own_authenticator(self):
        boss = self.sign_in_boss()
        UserMfa.objects.create(user=boss, secret_encrypted="x", confirmed_at=timezone.now())
        AuthSession.objects.filter(user=boss).update(mfa_verified_at=timezone.now())

        response = self.reset(boss.pk)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(UserMfa.objects.filter(user=boss).exists())

    def test_a_normal_admin_a_landlord_and_a_tenant_are_refused(self):
        ada = self.admin_with_authenticator()
        self.sign_in_as_admin(email="plain@example.com")
        statuses = [self.reset(ada.pk).status_code]
        for role in ("LANDLORD", "TENANT"):
            person = self.make_user(f"{role.lower()}@example.com", role)
            self.sign_in_user(person)
            statuses.append(self.reset(ada.pk).status_code)

        self.assertEqual(statuses, [403, 403, 403])
        self.assertTrue(UserMfa.objects.filter(user=ada).exists())

    def test_an_unknown_user_is_not_found(self):
        self.sign_in_boss()

        self.assertEqual(self.reset(999999).status_code, 404)

    def test_the_reset_still_happens_and_says_so_when_the_email_cannot_be_sent(self):
        ada = self.admin_with_authenticator()
        self.sign_in_boss()

        with mock.patch(SEND, side_effect=OSError("mail is down")):
            response = self.reset(ada.pk)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(response.data["notice_sent"])
        self.assertFalse(UserMfa.objects.filter(user=ada).exists())

    def test_the_detail_says_an_authenticator_was_reset_until_they_set_up_a_new_one(self):
        ada = self.admin_with_authenticator()
        self.sign_in_boss()
        self.assertFalse(self.was_reset(ada))

        self.reset(ada.pk)
        self.assertTrue(self.was_reset(ada))

        UserMfa.objects.create(user=ada, secret_encrypted="x", confirmed_at=timezone.now())
        self.assertFalse(self.was_reset(ada))

    def resend(self, user_id):
        return self.post(f"/api/users/{user_id}/resend-authenticator-notice/", {})

    def reset_by_boss(self):
        ada = self.admin_with_authenticator()
        self.sign_in_boss()
        with mock.patch(SEND, side_effect=OSError("mail is down")):
            self.reset(ada.pk)
        mail.outbox.clear()
        return ada

    def test_a_super_admin_sends_the_reset_email_again(self):
        ada = self.reset_by_boss()

        response = self.resend(ada.pk)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data["notice_sent"])
        self.assertEqual([m.to for m in mail.outbox], [["ada@example.com"]])
        self.assertEqual(mail.outbox[0].subject, "Your RentTrace authenticator was reset")

    def test_it_says_so_when_the_email_still_cannot_be_sent(self):
        ada = self.reset_by_boss()

        with mock.patch(SEND, side_effect=OSError("mail is down")):
            response = self.resend(ada.pk)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(response.data["notice_sent"])

    def test_someone_who_still_has_an_authenticator_is_refused(self):
        ada = self.admin_with_authenticator()
        self.sign_in_boss()
        mail.outbox.clear()

        self.assertEqual(self.resend(ada.pk).status_code, 400)
        self.assertEqual(mail.outbox, [])

    def test_someone_whose_authenticator_was_never_reset_is_refused(self):
        tess = self.make_user("tess@example.com")
        self.sign_in_boss()

        self.assertEqual(self.resend(tess.pk).status_code, 400)

    def test_resending_is_refused_for_a_normal_admin_a_landlord_and_a_tenant(self):
        ada = self.reset_by_boss()
        self.sign_in_as_admin(email="plain@example.com")
        mail.outbox.clear()
        statuses = [self.resend(ada.pk).status_code]
        for role in ("LANDLORD", "TENANT"):
            self.sign_in_user(self.make_user(f"{role.lower()}@example.com", role))
            statuses.append(self.resend(ada.pk).status_code)

        self.assertEqual(statuses, [403, 403, 403])
        self.assertNotIn("Your RentTrace authenticator was reset", [m.subject for m in mail.outbox])

    def test_resending_for_an_unknown_user_is_not_found(self):
        self.sign_in_boss()

        self.assertEqual(self.resend(999999).status_code, 404)
