from maintenance.services.shared.scope import find_issue


def get_issue(*, user, issue_id):
    return find_issue(user, issue_id)
