from django.core import mail
from django.utils import timezone

from accounts.models import AccountAccessHistory, AuthSession, MfaBackupCode, UserMfa
from users.tests.base import UsersApiTestCase

REASON = {"reason": "Confirmed by phone that it is really Ada. Lost her phone."}


class ResetAuthenticatorTests(UsersApiTestCase):
    def reset(self, user_id, data=REASON):
        return self.post(f"/api/users/{user_id}/reset-authenticator/", data)

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
