from .models import SiteVisit

def site_stats(request):
    return {
        "total_site_visits": SiteVisit.objects.count()
    }
