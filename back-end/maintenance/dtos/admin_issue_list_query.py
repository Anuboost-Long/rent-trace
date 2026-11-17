from rest_framework import serializers

from maintenance.dtos.issue_list_query import IssueListQueryDto


class AdminIssueListQueryDto(IssueListQueryDto):
    q = serializers.CharField(
        required=False, max_length=100, help_text="Matches the title, property name or suburb."
    )
