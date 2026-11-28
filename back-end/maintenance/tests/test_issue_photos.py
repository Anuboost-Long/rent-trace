import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from files.models import File
from maintenance.tests.base import URL, MaintenanceApiTestCase

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
ADMIN = "/api/admin/maintenance/"


class IssuePhotoTests(MaintenanceApiTestCase):
    def setUp(self):
        super().setUp()
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)

    def add_photo(self, issue, user, content=PNG, name="leak.png", **extra):
        self.as_user(user)
        return self.client.post(
            f"{URL}{issue['id']}/photos/",
            {"file": SimpleUploadedFile(name, content), **extra},
            format="multipart",
        )

    def test_the_tenant_adds_a_photo_and_it_shows_on_the_issue(self):
        issue = self.reported()

        response = self.add_photo(issue, self.tina, caption="Under the sink")

        self.assertEqual(response.status_code, 201, response.data)
        photo = response.data["photos"][0]
        self.assertEqual(
            (photo["name"], photo["caption"], photo["added_by"], photo["is_mine"]),
            ("leak.png", "Under the sink", "Tina Ray", True),
        )
        self.assertEqual(File.objects.get().uploaded_by, self.tina)

    def test_the_landlord_can_add_one_too_and_sees_whose_is_whose(self):
        issue = self.reported()
        self.add_photo(issue, self.tina)

        response = self.add_photo(issue, self.lou, JPEG, "after.jpg")

        mine = {p["name"]: p["is_mine"] for p in response.data["photos"]}
        self.assertEqual(mine, {"leak.png": False, "after.jpg": True})

    def test_only_jpeg_and_png_and_at_most_ten(self):
        issue = self.reported()

        self.assertEqual(self.add_photo(issue, self.tina, b"%PDF-1.4\n", "a.pdf").status_code, 400)
        for number in range(10):
            self.assertEqual(
                self.add_photo(issue, self.tina, name=f"{number}.png").status_code, 201
            )
        self.assertEqual(self.add_photo(issue, self.tina, name="eleventh.png").status_code, 400)
        self.assertEqual(File.objects.count(), 10)

    def test_a_closed_issue_takes_no_new_photos(self):
        issue = self.reported()
        self.propose(issue, self.tina)
        self.answer(issue, self.lou)

        self.assertEqual(self.add_photo(issue, self.tina).status_code, 400)

    def test_people_who_cannot_see_the_issue_get_a_404(self):
        issue = self.reported()
        self.assertEqual(self.add_photo(issue, self.sam).status_code, 404)
        self.assertEqual(
            self.add_photo(
                issue, self.make_user("m@example.com", "LANDLORD", "M", "C")
            ).status_code,
            404,
        )

    def test_the_photo_downloads_for_the_tenant_the_landlord_and_an_admin_only(self):
        issue = self.reported()
        file_id = self.add_photo(issue, self.tina).data["photos"][0]["id"]
        url = f"{URL}{issue['id']}/photos/{file_id}/"

        self.as_user(self.tina)
        opened = self.client.get(url)
        self.assertEqual((opened.status_code, opened["Content-Type"]), (200, "image/png"))
        self.assertEqual(b"".join(opened.streaming_content), PNG)
        self.as_user(self.lou)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.as_user(self.sam)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.sign_in_as_admin(email="admin@example.com")
        self.assertEqual(
            self.client.get(f"{ADMIN}{issue['id']}/photos/{file_id}/").status_code, 200
        )

    def test_only_the_person_who_added_a_photo_can_remove_it(self):
        issue = self.reported()
        file_id = self.add_photo(issue, self.tina).data["photos"][0]["id"]
        url = f"{URL}{issue['id']}/photos/{file_id}/"

        self.as_user(self.lou)
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.as_user(self.tina)
        removed = self.client.delete(url)

        self.assertEqual(removed.status_code, 200)
        self.assertEqual(removed.data["photos"], [])
        self.assertIsNotNone(File.objects.get(pk=file_id).deleted_at)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_a_photo_cannot_be_removed_once_the_issue_is_closed(self):
        issue = self.reported()
        file_id = self.add_photo(issue, self.tina).data["photos"][0]["id"]
        self.propose(issue, self.tina)
        self.answer(issue, self.lou)

        self.as_user(self.tina)
        self.assertEqual(
            self.client.delete(f"{URL}{issue['id']}/photos/{file_id}/").status_code, 400
        )
