from reviews.models import ReviewDecisionType, ReviewerSide, ReviewRoute

ESCALATE = "ESCALATE"


def name_of(person) -> str:
    return f"{person.first_name} {person.last_name}"


def landlord_rejection(report):
    return next(
        (d for d in report.decisions.all() if d.decision == ReviewDecisionType.REJECT), None
    )


def admin_decision(case):
    return next((d for d in case.decisions.all() if d.reviewer_side == ReviewerSide.ADMIN), None)


def escalation(case):
    """The history row written when someone asked an admin to decide; None when nobody did."""
    if case is None or case.review_route != ReviewRoute.ADMIN:
        return None
    return next((h for h in case.status_history.all() if h.action == ESCALATE), None)


def photos_of(report):
    submission = report.current_submission
    return [link.file for link in submission.files.all()] if submission else []


def place_of(report) -> str:
    place = report.target.condition_record.property_unit.property
    return place.property_name or f"{place.address_line_1}, {place.suburb}"
