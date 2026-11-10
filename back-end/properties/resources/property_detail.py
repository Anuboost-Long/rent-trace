from properties.resources.owner import OwnerResource
from properties.resources.property_file import PropertyFileResource
from properties.resources.property_summary import PropertySummaryResource
from properties.resources.unit import UnitResource


class PropertyDetailResource(PropertySummaryResource):
    owners = OwnerResource(source="current_owners", many=True)
    units = UnitResource(source="active_units", many=True)
    files = PropertyFileResource(source="active_files", many=True)

    class Meta(PropertySummaryResource.Meta):
        fields = [
            *PropertySummaryResource.Meta.fields,
            "public_description",
            "private_notes",
            "updated_at",
            "owners",
            "units",
            "files",
        ]
