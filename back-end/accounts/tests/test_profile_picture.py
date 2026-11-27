import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from accounts.models import AccountAccessHistory
from files.models import File
from tenancies.tests.base import TenancyApiTestCase

PICTURE = "/api/auth/profile/picture/"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64


class ProfilePictureTests(TenancyApiTestCase):
    def setUp(self):
        super().setUp()
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)
        self.tenancy = self.new_tenancy()
        self.add_tenant(self.tenancy["id"], self.tina)
        self.sam = self.make_user("sam@example.com", "TENANT", "Sam", "Fox")

    def upload(self, user, content=PNG, name="me.png"):
        self.as_user(user)
        return self.client.post(
            PICTURE, {"file": SimpleUploadedFile(name, content)}, format="multipart"
        )

    def view(self, viewer, target):
        self.as_user(viewer)
        return self.client.get(f"/api/auth/users/{target.pk}/picture/")

    def test_a_person_sets_a_picture_and_it_shows_on_their_profile(self):
        response = self.upload(self.tina)

        self.assertEqual(response.status_code, 200, response.data)
        stored = File.objects.get()
        self.assertEqual((response.data["picture_id"], stored.mime_type), (stored.pk, "image/png"))
        self.assertEqual(stored.uploaded_by, self.tina)
        history = AccountAccessHistory.objects.get(action="UPDATED_OWN_PICTURE")
        self.assertEqual(history.after_values, {"picture_id": stored.pk})
        self.as_user(self.tina)
        self.assertEqual(self.client.get("/api/auth/me/").data["picture_id"], stored.pk)

    def test_a_landlord_and_a_tenant_can_both_have_one(self):
        self.assertEqual(self.upload(self.lou, JPEG, "lou.jpg").status_code, 200)
        self.assertEqual(self.upload(self.tina).status_code, 200)

        self.assertEqual(File.objects.count(), 2)

    def test_a_new_picture_replaces_the_old_one_and_hides_it(self):
        first = self.upload(self.tina).data["picture_id"]

        second = self.upload(self.tina, JPEG, "new.jpg").data["picture_id"]

        self.assertNotEqual(first, second)
        old = File.objects.get(pk=first)
        self.assertIsNotNone(old.deleted_at)
        self.assertIsNone(File.objects.get(pk=second).deleted_at)
        self.assertEqual(self.view(self.tina, self.tina).status_code, 200)
        self.assertEqual(
            AccountAccessHistory.objects.get(
                action="UPDATED_OWN_PICTURE", before_values__picture_id=first
            ).after_values,
            {"picture_id": second},
        )

    def test_only_jpeg_and_png_images_are_accepted(self):
        self.assertEqual(
            self.upload(self.tina, b"%PDF-1.4\n" + b"\x00" * 32, "a.pdf").status_code, 400
        )
        self.assertEqual(self.upload(self.tina, b"hello", "note.png").status_code, 400)
        self.assertFalse(File.objects.exists())
        self.as_user(self.tina)
        self.assertIsNone(self.client.get("/api/auth/me/").data["picture_id"])

    def test_removing_it_clears_the_picture_and_is_harmless_when_there_is_none(self):
        self.as_user(self.tina)
        self.assertEqual(self.client.delete(PICTURE).status_code, 200)
        picture_id = self.upload(self.tina).data["picture_id"]

        response = self.client.delete(PICTURE)

        self.assertIsNone(response.data["picture_id"])
        self.assertIsNotNone(File.objects.get(pk=picture_id).deleted_at)
        self.assertTrue(AccountAccessHistory.objects.filter(action="REMOVED_OWN_PICTURE").exists())
        self.assertEqual(self.view(self.tina, self.tina).status_code, 404)

    def test_the_person_an_admin_and_people_they_share_a_tenancy_can_open_it(self):
        self.upload(self.tina)
        self.add_tenant(self.tenancy["id"], self.sam)

        opened = self.view(self.tina, self.tina)
        self.assertEqual((opened.status_code, opened["Content-Type"]), (200, "image/png"))
        self.assertEqual(b"".join(opened.streaming_content), PNG)
        self.assertEqual(self.view(self.sam, self.tina).status_code, 200)
        self.assertEqual(self.view(self.lou, self.tina).status_code, 200)
        self.sign_in_as_admin(email="admin@example.com")
        self.assertEqual(
            self.client.get(f"/api/auth/users/{self.tina.pk}/picture/").status_code, 200
        )

    def test_a_tenant_can_see_their_landlords_picture_but_a_stranger_cannot(self):
        self.upload(self.lou, JPEG, "lou.jpg")
        stranger = self.make_user("out@example.com", "TENANT", "Out", "Sider")

        self.assertEqual(self.view(self.tina, self.lou).status_code, 200)
        self.assertEqual(self.view(stranger, self.lou).status_code, 404)
        self.assertEqual(self.view(self.sam, self.lou).status_code, 404)

    def test_no_picture_or_no_such_person_is_a_404(self):
        self.assertEqual(self.view(self.tina, self.lou).status_code, 404)
        self.as_user(self.tina)
        self.assertEqual(self.client.get("/api/auth/users/99999/picture/").status_code, 404)

    def test_signing_in_is_required(self):
        self.client.credentials()
        self.assertIn(
            self.client.get(f"/api/auth/users/{self.tina.pk}/picture/").status_code, (401, 403)
        )
        self.assertIn(self.client.delete(PICTURE).status_code, (401, 403))
