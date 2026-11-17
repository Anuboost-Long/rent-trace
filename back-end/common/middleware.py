import hmac
import logging
import time
import uuid

from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger("renttrace.requests")

REQUEST_ID_HEADER = "X-Request-ID"
API_KEY_HEADER = "X-API-Key"
API_KEY_FAILURE_CODE = "invalid_api_key"
API_PREFIX = "/api/"
OPEN_PATHS = ("/api/docs/", "/api/schema/", "/api/redoc/")


def _level_for(status_code):
    if status_code >= 500:
        return logging.ERROR
    if status_code >= 400:
        return logging.WARNING
    return logging.INFO


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded_for.split(",")[0].strip() or request.META.get("REMOTE_ADDR", "-")


def _error_summary(response):
    data = getattr(response, "data", None) if response.status_code >= 400 else None
    if not isinstance(data, dict):
        return ""
    detail = data.get("detail")
    if isinstance(detail, str):
        return f' detail="{detail}"'
    return f" fields={sorted(data)}"


class RequestLogMiddleware:
    """Logs one line per request. Never logs the query string, headers or body. The IP comes from X-Forwarded-For when the
    Next server forwards it, so it is for tracing only and can be spoofed."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = uuid.uuid4().hex[:12]
        request.request_id = request_id
        started = time.monotonic()
        response = self.get_response(request)
        response[REQUEST_ID_HEADER] = request_id
        logger.log(
            _level_for(response.status_code),
            self._line(request, response.status_code, started) + _error_summary(response),
        )
        return response

    def _line(self, request, status_code, started):
        user = getattr(request, "user", None)
        user_id = getattr(user, "pk", None) or "-"
        elapsed_ms = round((time.monotonic() - started) * 1000)
        return (
            f"{request.method} {request.path} {status_code} {elapsed_ms}ms "
            f"user={user_id} ip={_client_ip(request)} req={request.request_id}"
        )


class ApiKeyMiddleware:
    """Every /api/ request must carry the server's API key in X-API-Key, signed in or not. With no
    API_KEY configured nothing gets through. The API docs pages stay open so they can load."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        needs_key = request.path.startswith(API_PREFIX) and not request.path.startswith(OPEN_PATHS)
        if needs_key and not self._has_valid_key(request):
            return JsonResponse(
                {"detail": "A valid API key is required.", "code": API_KEY_FAILURE_CODE},
                status=401,
            )
        return self.get_response(request)

    def _has_valid_key(self, request):
        expected = settings.API_KEY.encode()
        sent = request.headers.get(API_KEY_HEADER, "").encode()
        return bool(expected) and hmac.compare_digest(sent, expected)
