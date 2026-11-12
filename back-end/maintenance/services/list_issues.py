from maintenance.services.shared.scope import visible_issues


def list_issues(*, user, status=None):
    issues = visible_issues(user)
    if status:
        issues = issues.with_status(status)
    return issues.newest_first()
