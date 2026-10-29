from django.urls import path

from accounts import views

urlpatterns = [
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("resend-verification/", views.ResendVerificationView.as_view(), name="resend-verification"),
    path("sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("google/", views.GoogleSignInView.as_view(), name="google-sign-in"),
    path("refresh/", views.RefreshView.as_view(), name="refresh"),
    path("sign-out/", views.SignOutView.as_view(), name="sign-out"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("me/", views.MeView.as_view(), name="me"),
    path("onboarding/", views.OnboardingView.as_view(), name="onboarding"),
]
