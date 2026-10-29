from rest_framework.throttling import SimpleRateThrottle

from accounts.services.shared.account_rules import normalize_email


class _EmailThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        email = request.data.get("email")
        if not isinstance(email, str) or not email.strip():
            return None
        return f"throttle_{view.throttle_scope}_{self.window}_{normalize_email(email.strip())}"


class EmailPerMinuteThrottle(_EmailThrottle):
    rate = "1/min"
    window = "minute"


class EmailPerHourThrottle(_EmailThrottle):
    rate = "5/hour"
    window = "hour"
