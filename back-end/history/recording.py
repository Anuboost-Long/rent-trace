import json
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Max

TARGET_FIELDS = {
    "property": "property",
    "propertyunit": "property_unit",
    "tenancy": "tenancy",
    "conditionrecord": "condition_record",
}


def jsonable(values):
    """Decimals and dates as plain JSON, so a change reads the same wherever it is shown."""
    return json.loads(json.dumps(values, cls=DjangoJSONEncoder))


def changed_fields(record, changes):
    """The old and new values of only the fields that differ."""
    before, after = {}, {}
    for field, value in changes.items():
        old = getattr(record, field)
        if old != value:
            before[field], after[field] = old, value
    return before, after


def record_business_change(record, actor, action, before, after, reason, *, on_behalf_of=None):
    """One history row on the record's review target. Records of other kinds are skipped."""
    from history.models import BusinessChangeHistory
    from reviews.models import ReviewTarget

    link = TARGET_FIELDS.get(record._meta.model_name)
    if link is None or not after:
        return None
    audit = {"created_by": actor, "correlation_id": uuid.uuid4()}
    target = ReviewTarget.objects.get_or_create(**{link: record}, defaults=audit)[0]
    last = target.change_history.aggregate(last=Max("sequence_no"))["last"] or 0
    return BusinessChangeHistory.objects.create(
        target=target,
        sequence_no=last + 1,
        action=action,
        on_behalf_of=on_behalf_of,
        before_values=jsonable(before),
        after_values=jsonable(after),
        reason=reason,
        **audit,
    )
