from django.conf import settings
from django.core.checks import Warning, register

from accounts.security.signing_keys import MIN_KEY_BYTES


@register()
def jwt_signing_key_length(app_configs, **kwargs):
    if len(settings.JWT_SIGNING_KEY.encode()) >= MIN_KEY_BYTES:
        return []
    return [
        Warning(
            f"JWT_SIGNING_KEY is shorter than {MIN_KEY_BYTES} bytes, so access tokens are "
            "easier to forge.",
            hint="Run `python manage.py generate_jwt_key --write` and restart the server.",
            id="accounts.W001",
        )
    ]


@register()
def api_key_is_set(app_configs, **kwargs):
    if settings.API_KEY:
        return []
    return [
        Warning(
            "API_KEY is empty, so every /api/ request is rejected.",
            hint="Set API_KEY in config/.env and give the same value to the admin app.",
            id="accounts.W002",
        )
    ]
