from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

from properties.services.shared.property_files import find_property_file


def open_property_file(*, property_id, property_file_id, owned_by=None, unit_id=None):
    found = find_property_file(property_id, property_file_id, owned_by, unit_id)
    if not default_storage.exists(found.file.object_key):
        raise NotFound("This file is no longer available.")
    return found.file, default_storage.open(found.file.object_key, "rb")
