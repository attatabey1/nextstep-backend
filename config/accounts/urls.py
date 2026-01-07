from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
try:
    from ratelimit.decorators import ratelimit
except ImportError:
    def ratelimit(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator
from .views import signup

app_name = "accounts"

@method_decorator(ratelimit(key="ip", rate="5/m", block=True), name="dispatch")
class RateLimitedLoginView(auth_views.LoginView):
    pass

urlpatterns = [
    # --- Signup ---
    path("signup/", signup, name="signup"),

    # --- Login ---
    path(
        "login/",
        RateLimitedLoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),

    # --- Logout ---
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # --- Password reset ---
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
