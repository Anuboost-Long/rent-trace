from decimal import Decimal

from accounts.tests.base import TEST_API_KEY
from properties.models import Property, PropertyUnit
from properties.tests.test_property_files_api import LANDLORD_URL, PDF, FilesTestCase, upload

URL = "/api/public/listings/"


class PublicListingsTestCase(FilesTestCase):
    def listing(
        self,
        landlord=None,
        *,
        status="AVAILABLE",
        unit_public=True,
        rent=("650.00", "WEEKLY"),
        **property_fields,
    ):
        made = self.new_property(landlord or self.lou, **property_fields)
        unit_fields = {"name": "Room 1", "unit_type": "ROOM", "is_public": unit_public}
        if rent:
            unit_fields |= {"rent_amount": rent[0], "rent_frequency": rent[1]}
        unit = self.post(f"{LANDLORD_URL}{made['id']}/units/", unit_fields).data
        if status:
            self.client.post(
                f"{LANDLORD_URL}{made['id']}/listing/", {"listing_status": status}, format="json"
            )
        return made, unit

    def browse(self):
        self.client.credentials()


class BrowsingTests(PublicListingsTestCase):
    def test_anyone_can_browse_listed_properties_without_signing_in(self):
        made, _ = self.listing(suburb="Carlton")
        self.browse()

        response = self.client.get(URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.data["results"]], [made["id"]])

    def test_a_valid_api_key_is_still_required(self):
        self.listing()
        self.browse()
        del self.client.defaults["HTTP_X_API_KEY"]

        self.assertEqual(self.client.get(URL).status_code, 401)
        self.client.defaults["HTTP_X_API_KEY"] = TEST_API_KEY

    def test_a_stray_login_token_does_not_matter(self):
        self.listing()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")

        self.assertEqual(self.client.get(URL).status_code, 200)

    def test_only_listed_active_properties_with_a_public_unit_appear(self):
        shown, _ = self.listing(suburb="Shown")
        self.listing(suburb="Draft", status=None)
        self.listing(suburb="Unlisted", status="AVAILABLE")
        unlisted = Property.objects.get(suburb="Unlisted")
        self.client.post(
            f"{LANDLORD_URL}{unlisted.pk}/listing/", {"listing_status": "UNLISTED"}, format="json"
        )
        self.listing(suburb="Occupied", status="FULLY_OCCUPIED")
        archived, _ = self.listing(suburb="Archived")
        self.client.patch(
            f"{LANDLORD_URL}{archived['id']}/", {"property_status": "ARCHIVED"}, format="json"
        )
        partial, _ = self.listing(suburb="Partial", status="PARTIALLY_AVAILABLE")
        self.browse()

        response = self.client.get(URL, {"sort": "rent_low"})

        suburbs = sorted(row["suburb"] for row in response.data["results"])
        self.assertEqual(suburbs, ["Partial", "Shown"])
        self.assertEqual({shown["id"], partial["id"]}, {r["id"] for r in response.data["results"]})

    def test_nothing_private_is_ever_returned(self):
        made, _ = self.listing(
            private_notes="Key under the mat",
            address_line_1="12 Secret St",
            property_name="Hidden Gem",
        )
        self.browse()

        listing = self.client.get(URL).data["results"][0]
        detail = self.client.get(f"{URL}{made['id']}/").data

        text = str(listing) + str(detail)
        for secret in ("Key under the mat", "12 Secret St", "lou@example.com", "owner"):
            self.assertNotIn(secret, text)
        self.assertEqual(listing["title"], "Hidden Gem")
        self.assertEqual(
            {listing["suburb"], listing["state"], listing["postcode"]}, {"Fitzroy", "VIC", "3065"}
        )

    def test_the_title_falls_back_to_the_type_and_suburb(self):
        self.listing(suburb="Carlton")
        self.browse()

        self.assertEqual(self.client.get(URL).data["results"][0]["title"], "House in Carlton")


class DetailTests(PublicListingsTestCase):
    def test_the_detail_lists_public_units_and_hides_private_ones(self):
        made, _ = self.listing()
        self.post(
            f"{LANDLORD_URL}{made['id']}/units/",
            {"name": "Hidden room", "unit_type": "ROOM", "is_public": False},
        )
        self.browse()

        detail = self.client.get(f"{URL}{made['id']}/").data

        self.assertEqual([unit["name"] for unit in detail["units"]], ["Room 1"])
        self.assertEqual(detail["units"][0]["rent"], {"amount": "650.00", "frequency": "WEEKLY"})
        self.assertEqual(detail["unit_count"], 1)

    def test_the_detail_names_the_landlord_without_their_contact_details(self):
        made, _ = self.listing()
        self.browse()

        detail = self.client.get(f"{URL}{made['id']}/").data

        self.assertEqual(detail["listed_by"], "Lou R.")
        text = str(detail)
        for private in ("lou@example.com", "Reed", "phone"):
            self.assertNotIn(private, text)

    def test_the_summary_does_not_name_the_landlord(self):
        self.listing()
        self.browse()

        self.assertNotIn("listed_by", self.client.get(URL).data["results"][0])

    def test_an_unlisted_property_is_not_found(self):
        made, _ = self.listing(status=None)
        self.browse()

        self.assertEqual(self.client.get(f"{URL}{made['id']}/").status_code, 404)

    def test_the_cheapest_unit_sets_the_from_rent_across_frequencies(self):
        made, _ = self.listing(rent=("700.00", "WEEKLY"))
        self.post(
            f"{LANDLORD_URL}{made['id']}/units/",
            {
                "name": "Studio",
                "unit_type": "STUDIO",
                "is_public": True,
                "rent_amount": "2400.00",
                "rent_frequency": "MONTHLY",
            },
        )
        self.browse()

        row = self.client.get(URL).data["results"][0]

        self.assertEqual(row["from_rent"], {"amount": "2400.00", "frequency": "MONTHLY"})

    def test_a_listing_without_any_rent_has_no_from_rent(self):
        self.listing(rent=None)
        self.browse()

        self.assertIsNone(self.client.get(URL).data["results"][0]["from_rent"])


class FilterTests(PublicListingsTestCase):
    def setUp(self):
        super().setUp()
        self.cheap, _ = self.listing(suburb="Carlton", rent=("400.00", "WEEKLY"))
        self.mid, _ = self.listing(
            suburb="Richmond", rent=("2400.00", "MONTHLY"), property_type="APARTMENT"
        )
        self.dear, _ = self.listing(suburb="Carlton", rent=("900.00", "WEEKLY"), state="NSW")
        self.none, _ = self.listing(suburb="Fitzroy", rent=None)
        self.browse()

    def ids(self, **query):
        return [row["id"] for row in self.client.get(URL, query).data["results"]]

    def test_filters_by_state_suburb_and_type(self):
        self.assertEqual(self.ids(state="NSW"), [self.dear["id"]])
        self.assertEqual(
            sorted(self.ids(suburb="carlton")), sorted([self.cheap["id"], self.dear["id"]])
        )
        self.assertEqual(self.ids(type="APARTMENT"), [self.mid["id"]])

    def test_filters_by_weekly_rent_range_even_for_monthly_rents(self):
        self.assertEqual(self.ids(min_rent="500", max_rent="600"), [self.mid["id"]])
        self.assertEqual(self.ids(max_rent="450"), [self.cheap["id"]])
        self.assertEqual(
            sorted(self.ids(min_rent="500")), sorted([self.mid["id"], self.dear["id"]])
        )

    def test_sorts_by_rent_with_unpriced_listings_last(self):
        low = self.ids(sort="rent_low")
        high = self.ids(sort="rent_high")

        self.assertEqual(low, [self.cheap["id"], self.mid["id"], self.dear["id"], self.none["id"]])
        self.assertEqual(high, [self.dear["id"], self.mid["id"], self.cheap["id"], self.none["id"]])

    def test_newest_comes_first_by_default(self):
        self.assertEqual(self.ids()[0], self.none["id"])

    def test_text_search_matches_suburb_and_postcode(self):
        self.assertEqual(self.ids(q="richmond"), [self.mid["id"]])
        self.assertEqual(len(self.ids(q="3065")), 4)

    def test_bad_filters_are_rejected(self):
        self.assertEqual(self.client.get(URL, {"state": "XX"}).status_code, 400)
        self.assertEqual(self.client.get(URL, {"sort": "random"}).status_code, 400)
        self.assertEqual(self.client.get(URL, {"max_rent": "-1"}).status_code, 400)

    def test_results_are_paginated(self):
        page = self.client.get(URL, {"page_size": 2, "page": 2}).data

        self.assertEqual(
            (
                page["count"],
                page["page"],
                page["page_size"],
                page["total_pages"],
                len(page["results"]),
            ),
            (4, 2, 2, 2, 2),
        )


class PlacesTests(PublicListingsTestCase):
    def test_lists_only_places_with_listings_and_counts_them(self):
        self.listing(suburb="Carlton")
        self.listing(suburb="Carlton")
        self.listing(suburb="Bondi", state="NSW")
        self.listing(suburb="Hidden", status=None)
        self.browse()

        response = self.client.get(f"{URL}places/")

        self.assertEqual(
            response.data,
            [
                {"state": "NSW", "suburb": "Bondi", "listings": 1},
                {"state": "VIC", "suburb": "Carlton", "listings": 2},
            ],
        )


class PhotoTests(PublicListingsTestCase):
    def test_a_listed_propertys_photo_can_be_viewed_by_anyone(self):
        made, _ = self.listing()
        photo = self.send(f"{LANDLORD_URL}{made['id']}/files/", upload()).data
        self.browse()

        listing = self.client.get(URL).data["results"][0]
        response = self.client.get(f"{URL}{made['id']}/photos/{photo['id']}/")

        self.assertEqual(listing["cover_file_id"], photo["id"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("public", response["Cache-Control"])

    def test_documents_are_never_public(self):
        made, _ = self.listing()
        document = self.send(
            f"{LANDLORD_URL}{made['id']}/files/", upload(PDF, "deed.pdf", kind="DOCUMENT")
        ).data
        self.browse()

        self.assertEqual(
            self.client.get(f"{URL}{made['id']}/photos/{document['id']}/").status_code, 404
        )
        self.assertEqual(self.client.get(f"{URL}{made['id']}/").data["photos"], [])

    def test_photos_of_a_private_unit_are_hidden(self):
        made, public_unit = self.listing()
        private_unit = self.post(
            f"{LANDLORD_URL}{made['id']}/units/",
            {"name": "Hidden", "unit_type": "ROOM", "is_public": False},
        ).data
        shown = self.send(
            f"{LANDLORD_URL}{made['id']}/units/{public_unit['id']}/files/", upload()
        ).data
        hidden = self.send(
            f"{LANDLORD_URL}{made['id']}/units/{private_unit['id']}/files/", upload()
        ).data
        self.browse()

        detail = self.client.get(f"{URL}{made['id']}/").data

        self.assertEqual([p["id"] for p in detail["photos"]], [shown["id"]])
        self.assertEqual(detail["photos"][0]["unit_id"], public_unit["id"])
        self.assertEqual(
            self.client.get(f"{URL}{made['id']}/photos/{hidden['id']}/").status_code, 404
        )

    def test_the_propertys_own_cover_is_preferred_over_unit_photos(self):
        made, unit = self.listing()
        self.send(f"{LANDLORD_URL}{made['id']}/units/{unit['id']}/files/", upload())
        own = self.send(f"{LANDLORD_URL}{made['id']}/files/", upload()).data
        self.browse()

        self.assertEqual(self.client.get(URL).data["results"][0]["cover_file_id"], own["id"])

    def test_photos_of_an_unlisted_property_are_hidden(self):
        made, _ = self.listing(status=None)
        photo = self.send(f"{LANDLORD_URL}{made['id']}/files/", upload()).data
        self.browse()

        self.assertEqual(
            self.client.get(f"{URL}{made['id']}/photos/{photo['id']}/").status_code, 404
        )

    def test_the_rent_in_the_database_matches_what_is_shown(self):
        self.listing(rent=("123.45", "WEEKLY"))
        self.browse()

        row = self.client.get(URL).data["results"][0]

        self.assertEqual(Decimal(row["from_rent"]["amount"]), Decimal("123.45"))


class AvailableUnitsTests(PublicListingsTestCase):
    def add_unit(self, made, name, **fields):
        return self.post(
            f"{LANDLORD_URL}{made['id']}/units/",
            {"name": name, "unit_type": "ROOM", "is_public": True, **fields},
        ).data

    def test_only_vacant_and_partly_occupied_units_are_shown(self):
        made, vacant = self.listing(rent=("500", "WEEKLY"))
        partly = self.add_unit(made, "Partly", rent_amount="600", rent_frequency="WEEKLY")
        taken = self.add_unit(made, "Taken", rent_amount="100", rent_frequency="WEEKLY")
        off = self.add_unit(made, "Off", rent_amount="50", rent_frequency="WEEKLY")
        PropertyUnit.objects.filter(pk=partly["id"]).update(occupancy_status="PARTIALLY_OCCUPIED")
        PropertyUnit.objects.filter(pk=taken["id"]).update(occupancy_status="OCCUPIED")
        PropertyUnit.objects.filter(pk=off["id"]).update(occupancy_status="UNAVAILABLE")
        self.browse()

        detail = self.client.get(f"{URL}{made['id']}/").data
        row = self.client.get(URL).data["results"][0]

        self.assertEqual([unit["name"] for unit in detail["units"]], ["Room 1", "Partly"])
        self.assertEqual(detail["unit_count"], 2)
        self.assertEqual(row["from_rent"]["amount"], "500.00")
        self.assertEqual(self.client.get(URL, {"max_rent": "200"}).data["count"], 0)

    def test_a_listed_property_with_nothing_available_is_not_browsable(self):
        made, unit = self.listing()
        PropertyUnit.objects.filter(pk=unit["id"]).update(occupancy_status="OCCUPIED")
        self.browse()

        self.assertEqual(self.client.get(URL).data["count"], 0)
        self.assertEqual(self.client.get(f"{URL}{made['id']}/").status_code, 404)

    def test_each_unit_carries_its_own_photos_cover_first(self):
        made, first = self.listing()
        second = self.add_unit(made, "Room 2")
        base = f"{LANDLORD_URL}{made['id']}/units/"
        one = self.send(f"{base}{first['id']}/files/", upload()).data
        two = self.send(f"{base}{second['id']}/files/", upload()).data
        cover = self.send(f"{base}{second['id']}/files/", upload()).data
        self.client.patch(
            f"{base}{second['id']}/files/{cover['id']}/", {"is_cover": True}, format="json"
        )
        self.browse()

        units = {u["name"]: u for u in self.client.get(f"{URL}{made['id']}/").data["units"]}

        self.assertEqual([p["id"] for p in units["Room 1"]["photos"]], [one["id"]])
        self.assertEqual([p["id"] for p in units["Room 2"]["photos"]], [cover["id"], two["id"]])

    def test_photos_of_an_unavailable_unit_are_hidden(self):
        made, unit = self.listing()
        other = self.add_unit(made, "Taken")
        photo = self.send(f"{LANDLORD_URL}{made['id']}/units/{other['id']}/files/", upload()).data
        PropertyUnit.objects.filter(pk=other["id"]).update(occupancy_status="OCCUPIED")
        self.browse()

        self.assertEqual(self.client.get(f"{URL}{made['id']}/").data["photos"], [])
        self.assertEqual(
            self.client.get(f"{URL}{made['id']}/photos/{photo['id']}/").status_code, 404
        )
