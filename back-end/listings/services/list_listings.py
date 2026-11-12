from dataclasses import dataclass
from decimal import Decimal

from django.db.models import F, Q

from listings.services.shared.queries import listed_properties, with_public_details

ORDERING = {
    "newest": ("-created_at", "-id"),
    "rent_low": (F("weekly_rent").asc(nulls_last=True), "-id"),
    "rent_high": (F("weekly_rent").desc(nulls_last=True), "-id"),
}


@dataclass(frozen=True)
class ListingSearch:
    q: str | None = None
    state: str | None = None
    suburb: str | None = None
    property_type: str | None = None
    min_rent: Decimal | None = None
    max_rent: Decimal | None = None
    sort: str = "newest"


def list_listings(*, search):
    listings = _in_place(_matching_words(listed_properties(), search.q), search)
    listings = _in_rent_range(listings, search)
    return with_public_details(listings.order_by(*ORDERING[search.sort]))


def _matching_words(listings, text):
    for term in (text or "").split():
        listings = listings.filter(
            Q(property_name__icontains=term)
            | Q(suburb__icontains=term)
            | Q(postcode__icontains=term)
            | Q(public_description__icontains=term)
        )
    return listings


def _in_place(listings, search):
    if search.state:
        listings = listings.filter(state=search.state)
    if search.suburb:
        listings = listings.filter(suburb__iexact=search.suburb)
    if search.property_type:
        listings = listings.filter(property_type=search.property_type)
    return listings


def _in_rent_range(listings, search):
    if search.min_rent is not None:
        listings = listings.filter(weekly_rent__gte=search.min_rent)
    if search.max_rent is not None:
        listings = listings.filter(weekly_rent__lte=search.max_rent)
    return listings
