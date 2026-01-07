from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
try:
    from ratelimit.decorators import ratelimit
except ImportError:
    def ratelimit(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

from .models import ContactMessage, GalleryImage, GalleryLike
from listings.models import Listing, ListingView
from accounts.models import Profile


def services(request):
    """Services page view."""
    context = {
        "page_title": _("Our Services"),
        "description": _("Discover how SCHOLARIFY helps you find opportunities"),
        "services": [
            {
                "title": _("Opportunity Discovery"),
                "description": _("Find jobs, scholarships, and courses from verified sources worldwide."),
                "icon": "search",
                "color": "primary"
            },
            {
                "title": _("Application Guidance"),
                "description": _("Get help with application requirements, deadlines, and submission processes."),
                "icon": "bullhorn",
                "color": "secondary"
            },
            {
                "title": _("Community Support"),
                "description": _("Connect with peers, mentors, and experts in your field of interest."),
                "icon": "users",
                "color": "primary"
            },
        ]
    }
    return render(request, "pages/services.html", context)


def about(request):
    """About us page view."""
    context = {
        "page_title": _("About Us"),
        "description": _("Learn about SCHOLARIFY mission and team"),
        "team_members": [
            {
                "name": "Atta Tabee",
                "role": _("Founder & DHIS2 Expert"),
                "bio": _("Expert in DHIS2 with extensive experience in education technology."),
                "avatar": "AT"
            },
            {
                "name": _("Support Team"),
                "role": _("Academic Advisors"),
                "bio": _("Dedicated professionals helping students navigate opportunities."),
                "avatar": "ST"
            }
        ]
    }
    return render(request, "pages/about.html", context)


@ratelimit(key="ip", rate="10/m", block=True)
def contact(request):
    """Contact page view with form handling."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            messages.error(request, _("Please fill in name, email, and message."))
        else:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            messages.success(request, _("Your message was sent. We'll reply soon."))
            return redirect(request.path)

    context = {
        "page_title": _("Contact Us"),
        "description": _("Get in touch with our team"),
        "contact_info": {
            "phone": "+93 744 241 813",
            "email": "info@scholarify.af",
            "hours": _("Mon-Fri: 9AM-5PM"),
            "address": _("Kabul, Afghanistan")
        }
    }
    return render(request, "pages/contact.html", context)


def gallery(request):
    """Gallery page view showing all published images."""
    images = GalleryImage.objects.filter(is_published=True).order_by("-created_at")

    # Create session if doesn't exist
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    # Get likes count for all images
    likes_count = dict(
        GalleryLike.objects.filter(image__in=images)
        .values("image_id")
        .annotate(c=Count("id"))
        .values_list("image_id", "c")
    )

    # Get images liked by current user/session
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids.update(
            GalleryLike.objects.filter(image__in=images, user=request.user)
            .values_list("image_id", flat=True)
        )
    else:
        liked_ids.update(
            GalleryLike.objects.filter(image__in=images, session_key=session_key)
            .values_list("image_id", flat=True)
        )

    # Calculate total likes and views - NOW THIS WILL WORK
    total_likes = sum(likes_count.values())
    total_views = sum(img.views for img in images)

    context = {
        "page_title": _("Gallery"),
        "description": _("View our success stories and events"),
        "images": images,
        "likes_count": likes_count,
        "liked_ids": liked_ids,
        "total_likes": total_likes,
        "total_views": total_views,  # Now this will work with the views field
    }
    return render(request, "pages/gallery.html", context)


@require_POST
def gallery_like(request, pk):
    """Handle gallery image likes (AJAX)."""
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    image = get_object_or_404(GalleryImage, pk=pk, is_published=True)

    like_kwargs = {"image": image}
    if request.user.is_authenticated:
        like_kwargs["user"] = request.user
    else:
        like_kwargs["session_key"] = session_key

    # Check if already liked
    existing = GalleryLike.objects.filter(**like_kwargs)
    if existing.exists():
        existing.delete()
        liked = False
    else:
        GalleryLike.objects.create(**like_kwargs)
        liked = True

    # Get updated likes count
    likes = GalleryLike.objects.filter(image=image).count()
    
    return JsonResponse({"liked": liked, "likes": likes})


@staff_member_required
def dashboard(request):
    """Admin dashboard view (staff only)."""
    today = timezone.localdate()
    start_7 = today - timedelta(days=6)
    soon = today + timedelta(days=7)

    qs = Listing.objects.all()

    # Basic stats
    total_listings = qs.count()
    jobs = qs.filter(type="JOB").count()
    scholarships = qs.filter(type="SCHOLARSHIP").count()
    courses = qs.filter(type="COURSE").count()

    # Feature stats
    featured = qs.filter(is_featured=True).count()
    remote = qs.filter(remote=True).count()
    remote_pct = round((remote / total_listings) * 100, 1) if total_listings else 0

    # Deadline stats
    closing_soon = qs.filter(deadline__isnull=False, deadline__range=(today, soon)).count()
    expired = qs.filter(deadline__isnull=False, deadline__lt=today).count()

    # View stats
    total_listing_views = ListingView.objects.count()
    views_last_7_days = ListingView.objects.filter(date__gte=start_7).count()

    # Views by day (last 7 days)
    views_by_day_qs = (
        ListingView.objects.filter(date__gte=start_7)
        .values("date")
        .annotate(c=Count("id"))
        .order_by("date")
    )
    views_map = {row["date"]: row["c"] for row in views_by_day_qs}
    last7_dates = [start_7 + timedelta(days=i) for i in range(7)]
    views_labels = [d.strftime("%Y-%m-%d") for d in last7_dates]
    views_data = [views_map.get(d, 0) for d in last7_dates]

    # User gender stats
    male = Profile.objects.filter(gender="M").count()
    female = Profile.objects.filter(gender="F").count()
    na = Profile.objects.filter(gender="N").count()

    # Top countries
    top_countries = (
        qs.exclude(country__isnull=True)
        .exclude(country__exact="")
        .values("country")
        .annotate(c=Count("id"))
        .order_by("-c")[:8]
    )

    # Top viewed listings
    top_viewed_listings = (
        ListingView.objects.values("listing")
        .annotate(views=Count("id"))
        .order_by("-views")[:8]
    )
    
    # Convert listing IDs to objects
    listing_map = {l.id: l for l in Listing.objects.filter(id__in=[x["listing"] for x in top_viewed_listings])}
    top_viewed_listings = [
        {"listing": listing_map.get(x["listing"]), "views": x["views"]}
        for x in top_viewed_listings
        if listing_map.get(x["listing"]) is not None
    ]

    # Latest listings
    latest_listings = qs.order_by("-created_at")[:8] if hasattr(Listing, "created_at") else qs.order_by("-id")[:8]

    # Gallery stats
    gallery_images = GalleryImage.objects.filter(is_published=True).count()
    gallery_likes = GalleryLike.objects.count()
    gallery_views = sum(img.views for img in GalleryImage.objects.filter(is_published=True))
    
    # Contact messages stats
    contact_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    context = {
        "page_title": _("Dashboard"),
        "description": _("Admin dashboard for site management"),
        "today": today,
        "soon": soon,

        # Listing stats
        "total_listings": total_listings,
        "jobs": jobs,
        "scholarships": scholarships,
        "courses": courses,

        "featured": featured,
        "remote": remote,
        "remote_pct": remote_pct,

        "closing_soon": closing_soon,
        "expired": expired,

        # View stats
        "total_listing_views": total_listing_views,
        "views_last_7_days": views_last_7_days,
        "views_labels": views_labels,
        "views_data": views_data,

        # User stats
        "male": male,
        "female": female,
        "na": na,

        # Top content
        "top_countries": list(top_countries),
        "top_viewed_listings": top_viewed_listings,
        "latest_listings": latest_listings,

        # Other pages stats
        "gallery_images": gallery_images,
        "gallery_likes": gallery_likes,
        "gallery_views": gallery_views,  # Added gallery views
        "contact_messages": contact_messages,
        "unread_messages": unread_messages,
    }

    return render(request, "pages/dashboard.html", context)


# Additional optional views for future pages
def privacy(request):
    """Privacy policy page."""
    context = {
        "page_title": _("Privacy Policy"),
        "description": _("Learn how we protect your data"),
    }
    return render(request, "pages/privacy.html", context)


def terms(request):
    """Terms of service page."""
    context = {
        "page_title": _("Terms of Service"),
        "description": _("Our terms and conditions"),
    }
    return render(request, "pages/terms.html", context)


def cookies(request):
    """Cookie policy page."""
    context = {
        "page_title": _("Cookie Policy"),
        "description": _("How we use cookies"),
    }
    return render(request, "pages/cookies.html", context)


def faq(request):
    """Frequently Asked Questions page."""
    context = {
        "page_title": _("FAQ"),
        "description": _("Frequently asked questions"),
        "faqs": [
            {
                "question": _("How do I find opportunities?"),
                "answer": _("Use the search filters on the Browse page to find jobs, scholarships, and courses that match your profile.")
            },
            {
                "question": _("Is SCHOLARIFY free to use?"),
                "answer": _("Yes, all our services are completely free for users.")
            },
            {
                "question": _("How can I contact support?"),
                "answer": _("Use the Contact page or call us at +93 744 241 813 during business hours.")
            }
        ]
    }
    return render(request, "pages/faq.html", context)
