from rest_framework import serializers


class TenancyFiguresResource(serializers.Serializer):
    by_status = serializers.DictField(child=serializers.IntegerField())
    ending_soon = serializers.IntegerField()
    pending_invitations = serializers.IntegerField()
    expired_invitations = serializers.IntegerField()
