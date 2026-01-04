# config/admin.py
from django.contrib import admin

class CustomAdminSite(admin.AdminSite):
    site_title = "NextStep Admin Portal"
    site_header = "NextStep Administration"
    index_title = "Dashboard"
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps.
        Provides alphabetical sorting for cleaner navigation.
        """
        app_dict = self._build_app_dict(request, app_label)
        
        # Sort apps alphabetically
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort models alphabetically within each app
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'].lower())
        
        return app_list

# Monkey-patch the default admin site
# This applies our customizations to Django's default admin
# Jazzmin will still work with this approach
admin.site.__class__ = CustomAdminSite