from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Listing, SavedListing


def home(request):
    featured = (
        Listing.objects.filter(status=Listing.Status.ACTIVE, is_featured=True)
        .order_by("-created_at")[:6]
    )
    latest = (
        Listing.objects.filter(status=Listing.Status.ACTIVE)
        .order_by("-created_at")[:9]
    )
    return render(request, "listings/home.html", {"featured": featured, "latest": latest})

def listings_list(request):
    qs = Listing.objects.filter(status=Listing.Status.ACTIVE).order_by("-created_at")

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(organization__icontains=q) |
            Q(country__icontains=q) |
            Q(city__icontains=q) |
            Q(tags__icontains=q)
        )

    t = (request.GET.get("type") or "").strip()
    if t:
        qs = qs.filter(type=t)

    remote = (request.GET.get("remote") or "").strip()
    if remote in ("1", "true", "True", "yes", "YES"):
        qs = qs.filter(remote=True)

    deadline = (request.GET.get("deadline") or "").strip()
    if deadline == "soon":
        today = timezone.localdate()
        qs = qs.filter(deadline__isnull=False, deadline__gte=today).order_by("deadline")

    return render(request, "listings/list.html", {"items": qs})


def listing_detail(request, pk):
    item = get_object_or_404(Listing, pk=pk, status=Listing.Status.ACTIVE)

    saved = False
    if request.user.is_authenticated:
        saved = SavedListing.objects.filter(user=request.user, listing=item).exists()

    return render(request, "listings/detail.html", {"item": item, "saved": saved})


@login_required
@require_POST
def toggle_save_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    obj = SavedListing.objects.filter(user=request.user, listing=listing).first()
    if obj:
        obj.delete()
        saved = False
    else:
        SavedListing.objects.create(user=request.user, listing=listing)
        saved = True

    return JsonResponse({"saved": saved})
