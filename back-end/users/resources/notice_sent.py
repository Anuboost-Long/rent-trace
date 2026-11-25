from rest_framework import serializers

from users.resources.user_detail import UserDetailResource


class NoticeSentResource(serializers.Serializer):
    notice_sent = serializers.BooleanField(
        help_text="False when the email could not be sent. Try again from the user's page."
    )


class ResetAuthenticatorResource(UserDetailResource, NoticeSentResource):
    pass
