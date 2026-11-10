import shutil
import tempfile
from unittest.mock import patch

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from files.models import File
from properties.models import PropertyFile, PropertyOwner
from properties.services.shared import uploads
from properties.tests.test_landlord_properties_api import LandlordApiTestCase
from properties.tests.test_properties_api import URL as ADMIN_URL

LANDLORD_URL = "/api/landlord/properties/"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
PDF = b"%PDF-1.4\n" + b"\x00" * 64


def upload(content=PNG, name="front.png", kind="PHOTO", **extra):
    return {"file": SimpleUploadedFile(name, content), "kind": kind, **extra}


class FilesTestCase(LandlordApiTestCase):
    def setUp(self):
        super().setUp()
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)

    def send(self, url, data):
        return self.client.post(url, data, format="multipart")

    def landlord_property(self, landlord=None):
        made = self.new_property(landlord or self.lou)
        return made["id"], f"{LANDLORD_URL}{made['id']}/files/"


class LandlordUploadTests(FilesTestCase):
    def test_a_landlord_adds_a_photo_and_it_becomes_the_cover(self):
        _, url = self.landlord_property()

        response = self.send(url, upload(caption="Front of the house"))

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["kind"], "PHOTO")
        self.assertTrue(response.data["is_cover"])
        self.assertEqual(response.data["caption"], "Front of the house")
        self.assertEqual(response.data["mime_type"], "image/png")
        stored = File.objects.get()
        self.assertEqual((stored.uploaded_by, stored.upload_status), (self.lou, "READY"))
        self.assertEqual(stored.size_bytes, len(PNG))
        self.assertEqual(len(stored.sha256), 64)

    def test_only_the_first_photo_is_the_cover_and_documents_never_are(self):
        _, url = self.landlord_property()

        first = self.send(url, upload())
        second = self.send(url, upload(JPEG, "side.jpg"))
        document = self.send(url, upload(PDF, "deed.pdf", kind="DOCUMENT"))

        self.assertEqual(
            [first.data["is_cover"], second.data["is_cover"], document.data["is_cover"]],
            [True, False, False],
        )
        self.assertEqual(second.data["mime_type"], "image/jpeg")

    def test_the_file_type_is_checked_by_content_not_by_name_or_claimed_type(self):
        _, url = self.landlord_property()

        fake_photo = self.send(url, upload(b"just some text", "fake.png"))
        pdf_as_photo = self.send(url, upload(PDF, "doc.pdf", kind="PHOTO"))
        photo_as_document = self.send(url, upload(PNG, "pic.png", kind="DOCUMENT"))

        for response in (fake_photo, pdf_as_photo, photo_as_document):
            self.assertEqual(response.status_code, 400)
            self.assertIn("file", response.data)
        self.assertFalse(File.objects.exists())

    def test_empty_and_oversized_files_are_rejected(self):
        _, url = self.landlord_property()

        empty = self.send(url, upload(b"", "empty.png"))
        too_big = self.send(url, upload(PNG + b"\x00" * 10_000_000, "big.png"))

        self.assertEqual((empty.status_code, too_big.status_code), (400, 400))
        self.assertFalse(PropertyFile.objects.exists())

    def test_a_property_can_hold_only_so_many_photos(self):
        _, url = self.landlord_property()

        with patch.dict(uploads.LIMITS, {"PHOTO": 2}):
            self.send(url, upload())
            self.send(url, upload())
            response = self.send(url, upload())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PropertyFile.objects.count(), 2)

    def test_a_landlord_cannot_add_files_to_someone_elses_property(self):
        theirs, _ = self.landlord_property(self.amy)
        self.as_user(self.lou)

        response = self.send(f"{LANDLORD_URL}{theirs}/files/", upload())

        self.assertEqual(response.status_code, 404)
        self.assertFalse(File.objects.exists())

    def test_tenants_cannot_upload(self):
        _, url = self.landlord_property()
        self.as_user(self.make_user("tina@example.com", "TENANT"))

        self.assertEqual(self.send(url, upload()).status_code, 403)

    def test_files_show_up_on_the_property_detail(self):
        property_id, url = self.landlord_property()
        self.send(url, upload())
        self.send(url, upload(PDF, "deed.pdf", kind="DOCUMENT"))

        detail = self.client.get(f"{LANDLORD_URL}{property_id}/")

        self.assertEqual(
            [(f["kind"], f["original_name"]) for f in detail.data["files"]],
            [("PHOTO", "front.png"), ("DOCUMENT", "deed.pdf")],
        )


class LandlordManageTests(FilesTestCase):
    def setUp(self):
        super().setUp()
        self.property_id, self.url = self.landlord_property()
        self.first = self.send(self.url, upload()).data
        self.second = self.send(self.url, upload(JPEG, "side.jpg")).data

    def test_choosing_a_new_cover_moves_it(self):
        response = self.client.patch(
            f"{self.url}{self.second['id']}/", {"is_cover": True}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        covers = PropertyFile.objects.filter(is_cover=True)
        self.assertEqual([c.pk for c in covers], [self.second["id"]])

    def test_a_document_cannot_be_the_cover(self):
        document = self.send(self.url, upload(PDF, "deed.pdf", kind="DOCUMENT")).data

        response = self.client.patch(
            f"{self.url}{document['id']}/", {"is_cover": True}, format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_the_caption_can_be_changed_and_cleared(self):
        edited = self.client.patch(
            f"{self.url}{self.first['id']}/", {"caption": "Kitchen"}, format="json"
        )
        cleared = self.client.patch(
            f"{self.url}{self.first['id']}/", {"caption": ""}, format="json"
        )

        self.assertEqual(edited.data["caption"], "Kitchen")
        self.assertIsNone(cleared.data["caption"])

    def test_deleting_the_cover_promotes_the_next_photo(self):
        response = self.client.delete(f"{self.url}{self.first['id']}/")

        self.assertEqual(response.status_code, 204)
        remaining = self.client.get(f"{LANDLORD_URL}{self.property_id}/").data["files"]
        self.assertEqual([(f["id"], f["is_cover"]) for f in remaining], [(self.second["id"], True)])
        self.assertIsNotNone(
            File.objects.get(pk=PropertyFile.objects.get(pk=self.first["id"]).file_id).deleted_at
        )

    def test_someone_elses_file_cannot_be_changed_or_deleted(self):
        self.as_user(self.amy)

        edit = self.client.patch(f"{self.url}{self.first['id']}/", {"caption": "x"}, format="json")
        remove = self.client.delete(f"{self.url}{self.first['id']}/")

        self.assertEqual((edit.status_code, remove.status_code), (404, 404))
        self.assertIsNone(PropertyFile.objects.get(pk=self.first["id"]).deleted_at)


class ContentTests(FilesTestCase):
    def test_the_owner_can_view_the_file_with_the_right_type(self):
        _, url = self.landlord_property()
        added = self.send(url, upload(caption="x")).data

        response = self.client.get(f"{url}{added['id']}/content/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("front.png", response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), PNG)

    def test_other_landlords_cannot_view_it(self):
        _, url = self.landlord_property()
        added = self.send(url, upload()).data
        self.as_user(self.amy)

        self.assertEqual(self.client.get(f"{url}{added['id']}/content/").status_code, 404)

    def test_a_missing_file_on_disk_is_a_404_not_a_crash(self):
        _, url = self.landlord_property()
        added = self.send(url, upload()).data
        default_storage.delete(File.objects.get().object_key)

        self.assertEqual(self.client.get(f"{url}{added['id']}/content/").status_code, 404)


class AdminFilesTests(FilesTestCase):
    def make_admin_property(self):
        made = self.post(ADMIN_URL, self.payload(self.lou)).data
        return made["id"], f"{ADMIN_URL}{made['id']}/files/"

    def test_an_admin_adds_a_file_to_any_property_for_a_landlord(self):
        admin = self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        _, url = self.make_admin_property()

        response = self.send(url, upload())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(File.objects.get().uploaded_by, admin)

    def test_the_admin_can_manage_and_view_those_files(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        property_id, url = self.make_admin_property()
        added = self.send(url, upload()).data

        edited = self.client.patch(f"{url}{added['id']}/", {"caption": "Front"}, format="json")
        content = self.client.get(f"{url}{added['id']}/content/")
        detail = self.client.get(f"{ADMIN_URL}{property_id}/")
        removed = self.client.delete(f"{url}{added['id']}/")

        self.assertEqual(
            (edited.status_code, content.status_code, removed.status_code), (200, 200, 204)
        )
        self.assertEqual(len(detail.data["files"]), 1)

    def test_a_view_only_admin_can_read_but_not_change_files(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        property_id, url = self.make_admin_property()
        added = self.send(url, upload()).data
        self.make_role("VIEWER", ["properties.admin_view"])
        self.sign_in_as_admin(roles=("VIEWER",), email="viewer@example.com")

        self.assertEqual(self.client.get(f"{url}{added['id']}/content/").status_code, 200)
        self.assertEqual(self.send(url, upload()).status_code, 403)
        self.assertEqual(self.client.delete(f"{url}{added['id']}/").status_code, 403)

    def test_admin_uploads_do_not_need_to_own_the_property(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        _, url = self.make_admin_property()

        self.send(url, upload())

        self.assertEqual(PropertyOwner.objects.get().owner, self.lou)


class UnitFilesTests(FilesTestCase):
    def setUp(self):
        super().setUp()
        self.property_id, self.property_files_url = self.landlord_property()
        self.unit = self.new_unit(self.property_id)
        self.unit_files_url = f"{LANDLORD_URL}{self.property_id}/units/{self.unit['id']}/files/"

    def new_unit(self, property_id, name="Room 1"):
        response = self.post(
            f"{LANDLORD_URL}{property_id}/units/", {"name": name, "unit_type": "ROOM"}
        )
        self.assertEqual(response.status_code, 201)
        return response.data

    def test_a_unit_photo_belongs_to_the_unit_and_is_its_own_cover(self):
        property_photo = self.send(self.property_files_url, upload()).data

        unit_photo = self.send(self.unit_files_url, upload(JPEG, "room.jpg"))

        self.assertEqual(unit_photo.status_code, 201, unit_photo.data)
        self.assertEqual(unit_photo.data["unit_id"], self.unit["id"])
        self.assertTrue(unit_photo.data["is_cover"])
        self.assertTrue(PropertyFile.objects.get(pk=property_photo["id"]).is_cover)
        self.assertIsNone(property_photo["unit_id"])

    def test_the_property_page_lists_property_and_unit_files_with_their_unit(self):
        self.send(self.property_files_url, upload())
        self.send(self.unit_files_url, upload(JPEG, "room.jpg"))

        detail = self.client.get(f"{LANDLORD_URL}{self.property_id}/")

        self.assertEqual(
            sorted((f["original_name"], f["unit_id"]) for f in detail.data["files"]),
            [("front.png", None), ("room.jpg", self.unit["id"])],
        )

    def test_covers_are_kept_per_unit(self):
        other = self.new_unit(self.property_id, "Room 2")
        other_url = f"{LANDLORD_URL}{self.property_id}/units/{other['id']}/files/"
        first = self.send(self.unit_files_url, upload()).data
        second = self.send(self.unit_files_url, upload(JPEG, "b.jpg")).data
        elsewhere = self.send(other_url, upload()).data

        self.client.patch(
            f"{self.unit_files_url}{second['id']}/", {"is_cover": True}, format="json"
        )

        covers = {
            pf.pk: pf.is_cover for pf in PropertyFile.objects.filter(property_unit__isnull=False)
        }
        self.assertEqual(covers, {first["id"]: False, second["id"]: True, elsewhere["id"]: True})

    def test_a_unit_file_cannot_be_reached_through_the_property_routes_or_the_wrong_unit(self):
        unit_file = self.send(self.unit_files_url, upload()).data
        property_file = self.send(self.property_files_url, upload()).data
        other = self.new_unit(self.property_id, "Room 2")
        wrong_unit = f"{LANDLORD_URL}{self.property_id}/units/{other['id']}/files/"

        via_property = self.client.get(f"{self.property_files_url}{unit_file['id']}/content/")
        via_unit = self.client.get(f"{self.unit_files_url}{property_file['id']}/content/")
        via_wrong_unit = self.client.get(f"{wrong_unit}{unit_file['id']}/content/")
        edit = self.client.patch(
            f"{self.property_files_url}{unit_file['id']}/", {"caption": "x"}, format="json"
        )

        self.assertEqual(
            [r.status_code for r in (via_property, via_unit, via_wrong_unit, edit)],
            [404, 404, 404, 404],
        )

    def test_the_file_can_be_viewed_through_its_unit(self):
        added = self.send(self.unit_files_url, upload(caption="Bed")).data

        response = self.client.get(f"{self.unit_files_url}{added['id']}/content/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), PNG)

    def test_a_unit_on_another_property_or_another_landlord_is_not_found(self):
        mine_other = self.new_property(self.lou, suburb="Carlton")
        stranger = self.new_property(self.amy)
        their_unit = self.new_unit(stranger["id"])
        self.as_user(self.lou)

        wrong_property = self.send(
            f"{LANDLORD_URL}{mine_other['id']}/units/{self.unit['id']}/files/", upload()
        )
        not_theirs = self.send(
            f"{LANDLORD_URL}{stranger['id']}/units/{their_unit['id']}/files/", upload()
        )

        self.assertEqual((wrong_property.status_code, not_theirs.status_code), (404, 404))
        self.assertFalse(File.objects.exists())

    def test_limits_are_counted_for_each_scope_separately(self):
        with patch.dict(uploads.LIMITS, {"PHOTO": 1}):
            property_photo = self.send(self.property_files_url, upload())
            unit_photo = self.send(self.unit_files_url, upload())
            second_unit_photo = self.send(self.unit_files_url, upload())

        self.assertEqual(
            (property_photo.status_code, unit_photo.status_code, second_unit_photo.status_code),
            (201, 201, 400),
        )

    def test_deleting_a_unit_removes_its_files_but_not_the_propertys(self):
        kept = self.send(self.property_files_url, upload()).data
        gone = self.send(self.unit_files_url, upload()).data

        response = self.client.delete(f"{LANDLORD_URL}{self.property_id}/units/{self.unit['id']}/")

        self.assertEqual(response.status_code, 204)
        removed = PropertyFile.objects.get(pk=gone["id"])
        self.assertIsNotNone(removed.deleted_at)
        self.assertIsNotNone(removed.file.deleted_at)
        self.assertIsNone(PropertyFile.objects.get(pk=kept["id"]).deleted_at)
        detail = self.client.get(f"{LANDLORD_URL}{self.property_id}/")
        self.assertEqual([f["id"] for f in detail.data["files"]], [kept["id"]])

    def test_deleting_a_unit_cover_promotes_the_next_photo_of_that_unit_only(self):
        property_cover = self.send(self.property_files_url, upload()).data
        first = self.send(self.unit_files_url, upload()).data
        second = self.send(self.unit_files_url, upload(JPEG, "b.jpg")).data

        self.client.delete(f"{self.unit_files_url}{first['id']}/")

        self.assertTrue(PropertyFile.objects.get(pk=second["id"]).is_cover)
        self.assertTrue(PropertyFile.objects.get(pk=property_cover["id"]).is_cover)

    def test_an_admin_can_add_files_to_a_unit(self):
        self.sign_in_as_admin(super_admin=True, email="boss@example.com")
        made = self.post(ADMIN_URL, self.payload(self.lou)).data
        unit = self.post(
            f"{ADMIN_URL}{made['id']}/units/", {"name": "Room 1", "unit_type": "ROOM"}
        ).data

        response = self.send(f"{ADMIN_URL}{made['id']}/units/{unit['id']}/files/", upload())

        self.assertEqual((response.status_code, response.data["unit_id"]), (201, unit["id"]))
