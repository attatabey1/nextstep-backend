from django.urls import path
from .views import home, listings_list, listing_detail
from . import views

urlpatterns = [
    path("", home, name="home"),
    path("listings/", listings_list, name="listings_list"),
    path("listings/<int:pk>/", listing_detail, name="listing_detail"),
      path("listings/<int:pk>/save/", views.toggle_save_listing, name="toggle_save_listing"),
]
