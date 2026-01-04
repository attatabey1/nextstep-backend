from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("gallery/", views.gallery, name="gallery"),
    path("contact/", views.contact, name="contact"),
    path("gallery/<int:pk>/like/", views.gallery_like, name="gallery-like"),
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Optional pages for future
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("cookies/", views.cookies, name="cookies"),
    path("faq/", views.faq, name="faq"),
]