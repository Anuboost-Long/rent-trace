from rest_framework.exceptions import ValidationError

from properties.services.shared.queries import live_properties
from providers.models import ServiceCategory

OPTIONAL_TEXT = ("contact_name", "phone_number", "email", "website", "address", "description")
CONTACT_FIELDS = ("phone_number", "email", "website")
NESTED_FIELDS = ("category_codes", "properties")


def split_fields(fields):
    details = {k: v for k, v in fields.items() if k not in NESTED_FIELDS}
    for name in OPTIONAL_TEXT:
        if name in details:
            details[name] = details[name] or None
    return details


def ensure_reachable(details):
    if not any(details.get(name) for name in CONTACT_FIELDS):
        raise ValidationError(
            {"phone_number": "Add a phone number, email or website so the provider can be reached."}
        )


def find_categories(codes):
    found = ServiceCategory.objects.filter(code__in=codes, is_active=True)
    unknown = set(codes) - {category.code for category in found}
    if unknown:
        raise ValidationError(
            {"category_codes": f"Unknown categories: {', '.join(sorted(unknown))}."}
        )
    return list(found)


def find_owned_properties(owner, links):
    wanted = {link["property_id"] for link in links}
    owned = {p.pk: p for p in live_properties(owner).filter(pk__in=wanted)}
    missing = wanted - owned.keys()
    if missing:
        raise ValidationError(
            {
                "properties": "You can only link properties you own: "
                + ", ".join(map(str, sorted(missing)))
            }
        )
    return owned
