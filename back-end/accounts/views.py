from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts import dtos, resources, services
from accounts.security import tokens
from accounts.security.throttles import EmailPerHourThrottle, EmailPerMinuteThrottle

SIGN_UP_SENT = "Check your email to finish signing up."
RESET_SENT = "If an account exists for this email, we've sent a reset link."
VERIFICATION_SENT = "If this email needs verifying, we've sent a new link."


def _validated(serializer_class, request):
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def _device(request, data):
    return services.Device(
        name=data.get("device_name"),
        user_agent=request.META.get("HTTP_USER_AGENT"),
        ip_address=request.META.get("REMOTE_ADDR"),
    )


def _signed_in_response(signed_in):
    return Response(
        resources.SignedInResource(
            {
                "access_token": signed_in.access_token,
                "expires_in": int(tokens.ACCESS_TOKEN_LIFETIME.total_seconds()),
                "refresh_token": signed_in.refresh_token,
                "needs_onboarding": signed_in.needs_onboarding,
                "user": signed_in.user,
            }
        ).data
    )


def _message(detail, status=200):
    return Response({"detail": detail}, status=status)


class PublicView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]

    def get_authenticate_header(self, request):
        return 'Bearer realm="api"'


class EmailLinkView(PublicView):
    throttle_classes = [ScopedRateThrottle, EmailPerMinuteThrottle, EmailPerHourThrottle]


class SignUpView(PublicView):
    throttle_scope = "sign_up"

    @extend_schema(request=dtos.SignUpDto, responses={202: resources.MessageResource})
    def post(self, request):
        data = _validated(dtos.SignUpDto, request)
        services.sign_up(
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role_code=data["role"],
        )
        return _message(SIGN_UP_SENT, status=202)


class VerifyEmailView(PublicView):
    throttle_scope = "email_links"

    @extend_schema(request=dtos.TokenDto, responses=resources.MessageResource)
    def post(self, request):
        services.verify_email(_validated(dtos.TokenDto, request)["token"])
        return _message("Your email is verified. You can sign in now.")


class ResendVerificationView(EmailLinkView):
    throttle_scope = "email_links"

    @extend_schema(request=dtos.EmailDto, responses={202: resources.MessageResource})
    def post(self, request):
        services.resend_verification(_validated(dtos.EmailDto, request)["email"])
        return _message(VERIFICATION_SENT, status=202)


class SignInView(PublicView):
    throttle_scope = "sign_in"

    @extend_schema(request=dtos.SignInDto, responses=resources.SignedInResource)
    def post(self, request):
        data = _validated(dtos.SignInDto, request)
        return _signed_in_response(
            services.sign_in_with_password(
                email=data["email"], password=data["password"], device=_device(request, data)
            )
        )


class GoogleSignInView(PublicView):
    throttle_scope = "sign_in"

    @extend_schema(request=dtos.GoogleSignInDto, responses=resources.SignedInResource)
    def post(self, request):
        data = _validated(dtos.GoogleSignInDto, request)
        return _signed_in_response(
            services.sign_in_with_google(
                supabase_access_token=data["access_token"], device=_device(request, data)
            )
        )


class RefreshView(PublicView):
    throttle_scope = "refresh"

    @extend_schema(request=dtos.RefreshDto, responses=resources.SignedInResource)
    def post(self, request):
        return _signed_in_response(
            services.refresh(_validated(dtos.RefreshDto, request)["refresh_token"])
        )


class ForgotPasswordView(EmailLinkView):
    throttle_scope = "email_links"

    @extend_schema(request=dtos.EmailDto, responses={202: resources.MessageResource})
    def post(self, request):
        services.request_password_reset(_validated(dtos.EmailDto, request)["email"])
        return _message(RESET_SENT, status=202)


class ResetPasswordView(PublicView):
    throttle_scope = "email_links"

    @extend_schema(request=dtos.ResetPasswordDto, responses=resources.MessageResource)
    def post(self, request):
        data = _validated(dtos.ResetPasswordDto, request)
        services.reset_password(
            raw_token=data["token"],
            new_password=data["new_password"],
            sign_out_other_devices=data["sign_out_other_devices"],
        )
        return _message("Your password is changed. Sign in with your new password.")


class SignOutView(APIView):
    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        services.sign_out(request.auth)
        return Response(status=204)


class ChangePasswordView(APIView):
    @extend_schema(request=dtos.ChangePasswordDto, responses=resources.MessageResource)
    def post(self, request):
        data = _validated(dtos.ChangePasswordDto, request)
        services.change_password(
            user=request.user,
            session=request.auth,
            current_password=data["current_password"],
            new_password=data["new_password"],
            sign_out_other_devices=data["sign_out_other_devices"],
        )
        return _message("Your password is changed.")


class MeView(APIView):
    @extend_schema(responses=resources.UserResource)
    def get(self, request):
        return Response(resources.UserResource(request.user).data)


class OnboardingView(APIView):
    @extend_schema(request=dtos.OnboardingDto, responses=resources.UserResource)
    def post(self, request):
        data = _validated(dtos.OnboardingDto, request)
        services.complete_onboarding(
            user=request.user,
            first_name=data["first_name"],
            last_name=data["last_name"],
            role_code=data["role"],
        )
        return Response(resources.UserResource(request.user).data)

