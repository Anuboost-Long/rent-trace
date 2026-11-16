from rest_framework.exceptions import NotFound

from maintenance.services.shared.scope import NOT_FOUND, all_issues


def get_any_issue(*, issue_id):
    found = all_issues().filter(pk=issue_id).first()
    if found is None:
        raise NotFound(NOT_FOUND)
    return found
