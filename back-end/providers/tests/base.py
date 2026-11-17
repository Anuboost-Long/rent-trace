from properties.tests.test_landlord_properties_api import LandlordApiTestCase

URL = "/api/landlord/providers/"


class ProvidersApiTestCase(LandlordApiTestCase):
    def details(self, **extra):
        return {"business_name": "Smith Plumbing", "phone_number": "0400 111 222", **extra}

    def new_provider(self, landlord=None, **extra):
        self.as_user(landlord or self.lou)
        response = self.post(URL, self.details(**extra))
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def link(self, property_id, **extra):
        return {"property_id": property_id, "is_recommended": False, **extra}
