from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

from listings.services.get_listing import get_listing
from listings.services.shared.presentation import public_photos


def open_listing_photo(*, listing_id, file_id):
    listing = get_listing(listing_id=listing_id)
    photo = next((p for p in public_photos(listing) if p.pk == file_id), None)
    if photo is None or not default_storage.exists(photo.file.object_key):
        raise NotFound("This photo isn't available.")
    return photo.file, default_storage.open(photo.file.object_key, "rb")
