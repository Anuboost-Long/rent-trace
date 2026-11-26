from reviews.models import ReviewRequest, ReviewStatus


def list_review_cases(*, status=None):
    cases = ReviewRequest.objects.admin_cases().filter(status=status or ReviewStatus.PENDING_REVIEW)
    return cases.with_case_details().order_by("submitted_at", "id")
