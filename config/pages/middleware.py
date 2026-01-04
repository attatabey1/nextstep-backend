from django.utils import timezone
from .models import SiteVisit


class SiteVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ignore admin pages
        if request.path.startswith("/admin"):
            return response

        if not request.session.session_key:
            request.session.save()

        SiteVisit.objects.get_or_create(
            session_key=request.session.session_key,
            date=timezone.localdate()
        )

        return response
