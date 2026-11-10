from accounts.models import User
from users.resources.user_summary import UserSummaryResource


class UserDetailResource(UserSummaryResource):
    class Meta(UserSummaryResource.Meta):
        model = User
        fields = [*UserSummaryResource.Meta.fields, "phone_number", "auth_method"]
