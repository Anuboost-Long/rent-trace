import shutil
import tempfile
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from conditions.models import ConditionRecord
from files.models import File
from history.models import BusinessChangeHistory
from notifications.models import Notification
from reviews.models import RemovalEffect, ReviewRequest
from reviews.tests.base import ADMIN_URL, LANDLORD_URL, EvidenceApiTestCase

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


class DecideRemovalTests(EvidenceApiTestCase):
    def setUp(self):
        super().setUp()
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)

    def report_with_photo(self):
        evidence = self.submitted()
        self.as_user(self.tina)
        photo = self.client.post(
            f"{self.tenant_url}{evidence['id']}/photos/",
            {"file": SimpleUploadedFile("damp.png", PNG)},
            format="multipart",
        )
        return evidence, photo.data["photos"][0]["id"]

    def asked(self):
        evidence, photo_id = self.report_with_photo()
        record = self.record_of(evidence)
        request_id = self.ask_tenant_removal([record]).data["id"]
        self.sign_in_as_admin(email="admin@example.com")
        return evidence, record, photo_id, request_id

    def test_approving_hides_the_record_its_photos_and_the_reports_without_deleting_anything(self):
        evidence, record, photo_id, request_id = self.asked()

        response = self.decide_removal(request_id, "approve")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "APPROVED")
        hidden = ConditionRecord.objects.get(pk=record)
        self.assertIsNotNone(hidden.deleted_at)
        self.assertEqual(File.objects.get(pk=photo_id).deleted_by, response.wsgi_request.user)
        self.assertEqual(
            sorted(RemovalEffect.objects.values_list("effect", flat=True)),
            ["HIDE_FILE", "HIDE_RECORD"],
        )
        change = BusinessChangeHistory.objects.get(action="HIDE_RECORD")
        self.assertEqual(change.after_values, {"hidden": True})
        self.assertEqual(ReviewRequest.objects.filter(kind="EVIDENCE_REVIEW").count(), 1)

    def test_hidden_reports_and_photos_disappear_for_everyone(self):
        evidence, record, photo_id, request_id = self.asked()
        self.decide_removal(request_id, "approve")

        self.as_user(self.lou)
        listed = self.client.get(f"{LANDLORD_URL}?unit_id={self.unit.pk}")
        self.assertEqual(listed.data, [])
        self.assertEqual(self.client.get(f"{LANDLORD_URL}photos/{photo_id}/").status_code, 404)
        self.as_user(self.tina)
        self.assertEqual(self.client.get(self.tenant_url).data, [])
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        self.assertEqual(self.client.get(f"{ADMIN_URL}photos/{photo_id}/").status_code, 404)

    def test_leaving_the_descendants_alone_hides_only_the_record(self):
        evidence, photo_id = self.report_with_photo()
        request_id = self.ask_tenant_removal(
            [self.record_of(evidence)], include_descendants=False
        ).data["id"]
        self.sign_in_as_admin(email="admin@example.com")

        self.decide_removal(request_id, "approve")

        self.assertIsNone(File.objects.get(pk=photo_id).deleted_at)
        self.assertEqual(
            list(RemovalEffect.objects.values_list("effect", flat=True)), ["HIDE_RECORD"]
        )

    def test_rejecting_changes_nothing_and_a_reason_is_required(self):
        evidence, record, photo_id, request_id = self.asked()

        self.assertEqual(self.decide_removal(request_id, "reject", reason="  ").status_code, 400)
        response = self.decide_removal(request_id, "reject", reason="Keep the record.")

        self.assertEqual(response.data["status"], "REJECTED")
        self.assertIsNone(ConditionRecord.objects.get(pk=record).deleted_at)
        self.assertFalse(RemovalEffect.objects.exists())

    def test_a_removal_is_decided_once_and_a_retry_changes_nothing(self):
        _, _, _, request_id = self.asked()
        key = uuid.uuid4()
        self.decide_removal(request_id, "approve", key=key)

        self.assertEqual(self.decide_removal(request_id, "approve", key=key).status_code, 200)
        self.assertEqual(self.decide_removal(request_id, "reject").status_code, 400)
        self.assertEqual(BusinessChangeHistory.objects.filter(action="HIDE_RECORD").count(), 1)

    def test_the_asker_and_the_owners_are_told(self):
        _, _, _, request_id = self.asked()

        self.decide_removal(request_id, "approve")

        told = Notification.objects.filter(kind="DATA_REMOVAL_DECIDED")
        self.assertEqual({n.recipient for n in told}, {self.tina, self.lou})

    def test_the_asker_can_withdraw_until_it_is_decided(self):
        record = self.record_of(self.submitted())
        request_id = self.ask_tenant_removal([record]).data["id"]
        url = f"/api/tenant/tenancies/{self.tenancy['id']}/removal-requests/{request_id}/cancel/"

        self.assertEqual(self.post(url).data["status"], "CANCELLED")
        self.assertEqual(self.post(url).status_code, 400)
        self.sign_in_as_admin(email="admin@example.com")
        self.assertEqual(self.decide_removal(request_id, "approve").status_code, 400)

    def test_only_an_admin_with_the_permission_can_decide(self):
        record = self.record_of(self.submitted())
        request_id = self.ask_landlord_removal([record]).data["id"]

        self.assertEqual(self.decide_removal(request_id, "approve").status_code, 403)
