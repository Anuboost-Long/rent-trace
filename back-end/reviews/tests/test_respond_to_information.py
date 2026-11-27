import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from conditions.models import ConditionRecord
from notifications.models import Notification
from reviews.models import ReviewRequest, ReviewSubmissionFile
from reviews.tests.base import EvidenceApiTestCase

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


class RespondToInformationTests(EvidenceApiTestCase):
    def asked(self):
        evidence = self.submitted()
        self.assertEqual(self.ask(evidence).status_code, 200)
        return evidence

    def test_the_tenant_answers_and_the_report_goes_back_to_the_landlord(self):
        evidence = self.asked()

        response = self.respond(evidence, description="North wall, behind the bed.")

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["status"], "PENDING_REVIEW")
        self.assertEqual(response.data["revision_no"], 2)
        self.assertEqual(response.data["description"], "North wall, behind the bed.")
        self.assertEqual(response.data["title"], "Damp patch in the bedroom")
        report = ReviewRequest.objects.get()
        self.assertEqual(report.submissions.count(), 2)
        first, second = report.submissions.order_by("revision_no")
        self.assertEqual(
            first.proposed_condition_version.condition_description, "Wall near the window."
        )
        self.assertEqual(second.base_condition_version, first.proposed_condition_version)
        self.assertEqual(
            second.proposed_condition_version.supersedes_version, first.proposed_condition_version
        )
        self.assertEqual(second.reason, "The north wall, last Tuesday.")

    def test_the_owners_are_told_and_the_window_restarts(self):
        evidence = self.asked()
        self.expire(evidence)

        self.respond(evidence)

        sent = Notification.objects.get(recipient=self.lou, kind="CONDITION_EVIDENCE_INFO_PROVIDED")
        self.assertIn("The north wall, last Tuesday.", sent.body)
        self.as_user(self.lou)
        self.assertEqual(self.approve(evidence).status_code, 200)

    def test_approving_after_an_answer_accepts_the_newest_version(self):
        evidence = self.asked()
        self.respond(evidence, title="Damp patch behind the bed")

        self.approve(evidence)

        note = ConditionRecord.objects.get()
        self.assertEqual(note.accepted_version.version_no, 2)
        self.assertEqual(note.accepted_version.title, "Damp patch behind the bed")

    def test_a_message_is_required_and_only_while_it_is_waiting_for_the_tenant(self):
        evidence = self.submitted()
        self.assertEqual(self.respond(evidence).status_code, 400)
        self.ask(evidence)
        self.assertEqual(self.respond(evidence, message="  ").status_code, 400)
        self.assertEqual(self.respond(evidence).status_code, 200)
        self.assertEqual(self.respond(evidence).status_code, 400)

    def test_only_the_author_can_answer(self):
        evidence = self.asked()
        self.add_tenant(self.tenancy["id"], self.sam)

        self.assertEqual(self.respond(evidence, user=self.sam).status_code, 404)

    def test_photos_carry_over_and_new_ones_can_be_added_first(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)
        evidence = self.submitted()
        self.as_user(self.tina)
        photos_url = f"{self.tenant_url}{evidence['id']}/photos/"
        self.client.post(photos_url, {"file": SimpleUploadedFile("a.png", PNG)}, format="multipart")
        self.ask(evidence)
        self.as_user(self.tina)
        added = self.client.post(
            photos_url, {"file": SimpleUploadedFile("b.png", PNG)}, format="multipart"
        )
        self.assertEqual(added.status_code, 201)

        response = self.respond(evidence)

        self.assertEqual(sorted(p["name"] for p in response.data["photos"]), ["a.png", "b.png"])
        self.assertEqual(ReviewSubmissionFile.objects.count(), 2 + 2)
