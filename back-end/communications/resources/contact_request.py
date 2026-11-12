from rest_framework import serializers

from communications.models import ContactRequest, ContactRequestStatus
from communications.services.shared.presentation import listing_title, primary_owner

FIELDS = ["id", "status", "message", "created_at", "decided_at", "listing", "unit"]


class ContactRequestBase(serializers.ModelSerializer):
    listing = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    def get_listing(self, contact_request) -> dict:
        place = contact_request.property
        return {
            "id": place.pk,
            "title": listing_title(contact_request),
            "suburb": place.suburb,
            "state": place.state,
        }

    def get_unit(self, contact_request) -> dict | None:
        unit = contact_request.property_unit
        return {"id": unit.pk, "name": unit.name} if unit else None


class TenantContactRequestResource(ContactRequestBase):
    landlord = serializers.SerializerMethodField(help_text="Only once the request is accepted.")

    class Meta:
        model = ContactRequest
        fields = [*FIELDS, "landlord"]

    def get_landlord(self, contact_request) -> dict | None:
        owner = primary_owner(contact_request)
        if contact_request.status != ContactRequestStatus.ACCEPTED or owner is None:
            return None
        return {
            "name": f"{owner.first_name} {owner.last_name}",
            "email": owner.email,
            "phone_number": owner.phone_number,
        }


class LandlordContactRequestResource(ContactRequestBase):
    tenant = serializers.SerializerMethodField()
    tenant_contact = serializers.SerializerMethodField(
        help_text="Only once the request is accepted."
    )

    class Meta:
        model = ContactRequest
        fields = [*FIELDS, "tenant", "tenant_contact"]

    def get_tenant(self, contact_request) -> dict:
        tenant = contact_request.tenant
        return {"id": tenant.pk, "first_name": tenant.first_name, "last_name": tenant.last_name}

    def get_tenant_contact(self, contact_request) -> dict | None:
        if contact_request.status != ContactRequestStatus.ACCEPTED:
            return None
        tenant = contact_request.tenant
        return {"email": tenant.email, "phone_number": tenant.phone_number}


class TenantContactRequestPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = TenantContactRequestResource(many=True)


class LandlordContactRequestPageResource(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    results = LandlordContactRequestResource(many=True)
