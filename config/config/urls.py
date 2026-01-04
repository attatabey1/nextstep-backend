"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


def root_redirect(request):
    """
    Redirect root URL to appropriate language version.
    Defaults to English unless user has selected Pashto.
    """
    lang = request.COOKIES.get("django_language", "en")
    if lang not in ("en", "ps"):
        lang = "en"
    return redirect(f"/{lang}/")


# Base URL patterns (language independent)
urlpatterns = [
    # Language switch endpoint - required for language switching
    path("i18n/", include("django.conf.urls.i18n")),
    
    # Root redirect - redirects to appropriate language version
    path("", root_redirect, name="root-redirect"),
]

# Language-specific URL patterns
# These will have language prefix (/en/, /ps/)
urlpatterns += i18n_patterns(
    # ✅ Using Django's default admin site (patched by config/admin.py)
    path("admin/", admin.site.urls),
    
    # Accounts app with namespace
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    
    # Pages app with namespace
    path("", include(("pages.urls", "pages"), namespace="pages")),
    
    # Listings app
    path("", include("listings.urls")),
    
    # You can add more apps here as needed
    # Example: path("blog/", include("blog.urls")),
)

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
# Serve uploaded media files in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ============================================
# ERROR HANDLERS (For Production)
# ============================================

# Uncomment these when you create the views
"""
handler400 = 'pages.views.custom_400_view'  # Bad Request
handler403 = 'pages.views.custom_403_view'  # Permission Denied
handler404 = 'pages.views.custom_404_view'  # Page Not Found
handler500 = 'pages.views.custom_500_view'  # Server Error
"""