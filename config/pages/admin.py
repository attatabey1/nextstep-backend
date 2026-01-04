from django.contrib import admin
from django.utils import timezone
from .models import ContactMessage, GalleryImage, GalleryLike, SiteVisit

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read', 'replied', 'replied_at')
    list_filter = ('is_read', 'replied', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'replied_at')
    list_editable = ('is_read', 'replied')
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status & Tracking', {
            'fields': ('is_read', 'replied', 'created_at', 'replied_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_replied', 'mark_as_not_replied']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(replied=True, replied_at=timezone.now())
    mark_as_replied.short_description = "Mark as replied (set timestamp)"
    
    def mark_as_not_replied(self, request, queryset):
        queryset.update(replied=False, replied_at=None)
    mark_as_not_replied.short_description = "Mark as not replied"

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'views', 'likes_count', 'is_published', 'order', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'caption')
    list_editable = ('order', 'is_published')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'caption', 'image', 'views')
        }),
        ('Settings', {
            'fields': ('order', 'is_published')
        }),
    )
    
    readonly_fields = ('views', 'created_at')
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="height: 50px; border-radius: 5px;" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"
    
    actions = ['publish_images', 'unpublish_images']
    
    def publish_images(self, request, queryset):
        queryset.update(is_published=True)
    publish_images.short_description = "Publish selected images"
    
    def unpublish_images(self, request, queryset):
        queryset.update(is_published=False)
    unpublish_images.short_description = "Unpublish selected images"

@admin.register(GalleryLike)
class GalleryLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'user_info', 'session_info', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('image__title', 'user__username', 'session_key')
    readonly_fields = ('created_at',)
    
    def user_info(self, obj):
        if obj.user:
            return obj.user.username
        return "Anonymous"
    user_info.short_description = "User"
    
    def session_info(self, obj):
        if obj.session_key:
            return f"{obj.session_key[:10]}..."
        return "No session"
    session_info.short_description = "Session"

@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ('session_display', 'date', 'visits_count')
    list_filter = ('date',)
    search_fields = ('session_key',)
    readonly_fields = ('session_key', 'date')
    
    # Remove add and change permissions since these are auto-generated
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def session_display(self, obj):
        return f"{obj.session_key[:15]}..." if obj.session_key else "No session"
    session_display.short_description = "Session ID"
    
    def visits_count(self, obj):
        # Count how many visits this session has
        return SiteVisit.objects.filter(session_key=obj.session_key).count()
    visits_count.short_description = "Total Visits"