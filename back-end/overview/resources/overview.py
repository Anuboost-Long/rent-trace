from rest_framework import serializers

from overview.resources.activity_entry import ActivityEntryResource
from overview.resources.people_figures import PeopleFiguresResource
from overview.resources.property_figures import PropertyFiguresResource
from overview.resources.tenancy_figures import TenancyFiguresResource


class OverviewResource(serializers.Serializer):
    """Each block is null when the person lacks the permission that shows it."""

    people = PeopleFiguresResource(allow_null=True)
    properties = PropertyFiguresResource(allow_null=True)
    tenancies = TenancyFiguresResource(allow_null=True)
    active_bans = serializers.IntegerField(allow_null=True)
    activity = ActivityEntryResource(many=True, allow_null=True)
