from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        from accounts.security import checks  # noqa: F401  registers the system checks
