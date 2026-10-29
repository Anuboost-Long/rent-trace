from rest_framework import serializers

SELF_SERVICE_ROLES = ["TENANT", "LANDLORD"]


class PasswordField(serializers.CharField):
    def __init__(self, **kwargs):
        super().__init__(max_length=128, trim_whitespace=False, style={"input_type": "password"}, **kwargs)
