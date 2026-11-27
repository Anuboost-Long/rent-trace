import uuid

from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from accounts.services.shared import account_management as manage
from accounts.services.shared.pictures import hide_file
from files.models import File, UploadStatus
from properties.models import PropertyFileKind
from properties.services.shared.uploads import check_upload, sha256_of


def set_profile_picture(*, user, upload):
    mime_type, extension = check_upload(upload, PropertyFileKind.PHOTO)
    checksum = sha256_of(upload)
    key = default_storage.save(f"profiles/{user.pk}/{uuid.uuid4().hex}.{extension}", upload)
    try:
        return _record(user, upload, key, mime_type, checksum)
    except Exception:
        default_storage.delete(key)
        raise


@transaction.atomic
def _record(user, upload, key, mime_type, checksum):
    now = timezone.now()
    target = (
        User.objects.select_for_update(of=("self",)).select_related("avatar_file").get(pk=user.pk)
    )
    before = target.avatar_file
    stored = File.objects.create(
        original_name=upload.name[:255],
        object_key=key,
        mime_type=mime_type,
        size_bytes=upload.size,
        sha256=checksum,
        upload_status=UploadStatus.READY,
        uploaded_by=target,
        created_by=target,
    )
    if before is not None:
        hide_file(before, target, now)
    target.avatar_file = stored
    manage.save_change(target, target, now)
    manage.record_change(
        actor=target,
        target=target,
        action="UPDATED_OWN_PICTURE",
        before={"picture_id": before.pk if before else None},
        after={"picture_id": stored.pk},
        reason="Profile picture changed by the account holder",
    )
    return target
