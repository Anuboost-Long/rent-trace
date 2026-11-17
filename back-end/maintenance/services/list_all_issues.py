from maintenance.services.shared.scope import all_issues


def list_all_issues(*, status=None, q=None):
    issues = all_issues()
    if status:
        issues = issues.with_status(status)
    if q:
        issues = issues.matching(q)
    return issues.newest_first()
