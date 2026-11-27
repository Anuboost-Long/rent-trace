import shutil
import tempfile

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from files.models import File
from reviews.models import ReviewSubmissionFile
from reviews.tests.base import ADMIN_URL, LANDLORD_URL, EvidenceApiTestCase

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
PDF = b"%PDF-1.4\n" + b"\x00" * 64


class EvidencePhotoTests(EvidenceApiTestCase):
    def setUp(self):
        super().setUp()
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(lambda: default_storage._wrapped.__init__())

    def photos_url(self, evidence):
        return f"{self.tenant_url}{evidence['id']}/photos/"

    def attach(self, evidence, content=PNG, name="damp.png", user=None):
        self.as_user(user or self.tina)
        upload = SimpleUploadedFile(name, content)
        return self.client.post(self.photos_url(evidence), {"file": upload}, format="multipart")

    def test_the_author_adds_a_photo_and_it_is_listed_on_the_report(self):
        evidence = self.submitted()

        response = self.attach(evidence)

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual([p["name"] for p in response.data["photos"]], ["damp.png"])
        stored = File.objects.get()
        self.assertEqual(stored.mime_type, "image/png")
        self.assertEqual(ReviewSubmissionFile.objects.get().file, stored)

    def test_only_images_are_accepted(self):
        evidence = self.submitted()

        self.assertEqual(self.attach(evidence, PDF, "plan.pdf").status_code, 400)
        self.assertEqual(self.attach(evidence, b"hello", "note.png").status_code, 400)
        self.assertFalse(File.objects.exists())

    def test_a_report_holds_five_photos(self):
        evidence = self.submitted()
        for number in range(5):
            self.assertEqual(self.attach(evidence, name=f"{number}.png").status_code, 201)

        self.assertEqual(self.attach(evidence, name="sixth.png").status_code, 400)
        self.assertEqual(File.objects.count(), 5)

    def test_photos_cannot_be_added_once_it_is_answered_withdrawn_or_expired(self):
        answered = self.submitted()
        self.approve(answered)
        self.assertEqual(self.attach(answered).status_code, 400)
        expired = self.submitted()
        self.expire(expired)
        self.assertEqual(self.attach(expired).status_code, 400)
        withdrawn = self.submitted()
        self.as_user(self.tina)
        self.post(f"{self.tenant_url}{withdrawn['id']}/cancel/")
        self.assertEqual(self.attach(withdrawn).status_code, 400)

    def test_only_the_author_can_add_one(self):
        evidence = self.submitted()
        self.add_tenant(self.tenancy["id"], self.sam)

        self.assertEqual(self.attach(evidence, user=self.sam).status_code, 404)

    def open_as(self, user, url):
        self.as_user(user)
        return self.client.get(url)

    def test_the_author_the_landlord_and_an_admin_can_open_it_but_nobody_else(self):
        evidence = self.submitted()
        photo = self.attach(evidence).data["photos"][0]
        self.add_tenant(self.tenancy["id"], self.sam)
        tenant_url = f"{self.tenant_url}photos/{photo['id']}/"
        landlord_url = f"{LANDLORD_URL}photos/{photo['id']}/"

        mine = self.open_as(self.tina, tenant_url)
        self.assertEqual((mine.status_code, mine["Content-Type"]), (200, "image/png"))
        self.assertEqual(b"".join(mine.streaming_content), PNG)
        self.assertEqual(self.open_as(self.lou, landlord_url).status_code, 200)
        self.assertEqual(self.open_as(self.mia, landlord_url).status_code, 404)
        self.assertEqual(self.open_as(self.sam, tenant_url).status_code, 404)
        self.sign_in_as_admin(email="admin@example.com")
        self.assertEqual(self.client.get(f"{ADMIN_URL}photos/{photo['id']}/").status_code, 200)

    def test_the_landlord_sees_the_photos_on_the_report_and_an_admin_on_the_case(self):
        evidence = self.submitted()
        self.attach(evidence)
        self.reject(evidence)
        self.escalate(evidence, self.tina)

        self.as_user(self.lou)
        as_landlord = self.client.get(f"{LANDLORD_URL}?unit_id={self.unit.pk}")
        self.assertEqual(as_landlord.data[0]["photos"][0]["name"], "damp.png")
        self.sign_in_as_admin(email="admin@example.com")
        cases = self.client.get(ADMIN_URL)
        self.assertEqual(cases.data["results"][0]["photos"][0]["name"], "damp.png")
