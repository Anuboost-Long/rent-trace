from documents.tests.base import ADMIN_URL, LANDLORD_URL, PNG, DocumentApiTestCase


class ListDocumentsTests(DocumentApiTestCase):
    def test_each_side_and_an_admin_see_the_document(self):
        document = self.published()

        landlord = self.client.get(f"{LANDLORD_URL}?unit_id={self.unit.pk}")
        detail = self.client.get(f"{LANDLORD_URL}{document['id']}/")
        self.as_user(self.tina)
        tenant = self.client.get(self.tenant_url)
        tenant_detail = self.client.get(f"{self.tenant_url}{document['id']}/")
        self.sign_in_as_admin(email="admin@example.com")
        admin = self.client.get(f"{ADMIN_URL}?unit_id={self.unit.pk}")
        admin_detail = self.client.get(f"{ADMIN_URL}{document['id']}/")

        for response in (landlord, tenant, admin):
            self.assertEqual([d["id"] for d in response.data], [document["id"]])
        for response in (detail, tenant_detail, admin_detail):
            self.assertEqual(response.data["versions"][0]["title"], "Tenancy agreement")

    def test_other_people_do_not_see_it(self):
        document = self.published()
        self.add_tenant(self.tenancy["id"], self.sam)
        outsider = self.make_user("out@example.com", "TENANT", "Out", "Sider")

        self.as_user(self.mia)
        self.assertEqual(self.client.get(f"{LANDLORD_URL}?unit_id={self.unit.pk}").status_code, 404)
        self.assertEqual(self.client.get(f"{LANDLORD_URL}{document['id']}/").status_code, 404)
        self.as_user(outsider)
        self.assertEqual(self.client.get(self.tenant_url).status_code, 404)
        self.as_user(self.lou)
        self.assertEqual(self.client.get(f"{ADMIN_URL}?unit_id={self.unit.pk}").status_code, 403)

    def test_a_tenant_sees_only_documents_on_their_own_tenancy(self):
        self.published(document_type="NOTICE", title="Notice")
        self.published(document_type="OTHER", title="Unit papers", tenancy_id="")
        self.as_user(self.tina)

        titles = [d["versions"][0]["title"] for d in self.client.get(self.tenant_url).data]

        self.assertEqual(titles, ["Notice"])

    def test_the_file_opens_for_the_owner_the_tenant_and_an_admin_only(self):
        document = self.published(file=self.pdf("scan.png", PNG))
        file_id = document["versions"][0]["files"][0]["id"]
        self.add_tenant(self.tenancy["id"], self.sam)
        outsider = self.make_user("out@example.com", "TENANT", "Out", "Sider")
        landlord_url = f"{LANDLORD_URL}files/{file_id}/"
        tenant_url = f"{self.tenant_url}files/{file_id}/"

        self.as_user(self.lou)
        opened = self.client.get(landlord_url)
        self.assertEqual((opened.status_code, opened["Content-Type"]), (200, "image/png"))
        self.assertEqual(b"".join(opened.streaming_content), PNG)
        self.as_user(self.tina)
        self.assertEqual(self.client.get(tenant_url).status_code, 200)
        self.as_user(self.mia)
        self.assertEqual(self.client.get(landlord_url).status_code, 404)
        self.as_user(outsider)
        self.assertEqual(self.client.get(tenant_url).status_code, 404)
        self.sign_in_as_admin(email="admin@example.com")
        self.assertEqual(self.client.get(f"{ADMIN_URL}files/{file_id}/").status_code, 200)
