from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone  # Added this import


class GalleryImage(models.Model):
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to="gallery/")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)  # ADDED THIS FIELD
    
    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title or f"Gallery Image {self.id}"

    def increment_views(self):
        """Increment the view count for this image."""
        self.views += 1
        self.save(update_fields=['views'])


class GalleryLike(models.Model):
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["image", "user"],
                condition=Q(user__isnull=False),
                name="unique_like_per_user_per_image",
            ),
            models.UniqueConstraint(
                fields=["image", "session_key"],
                condition=Q(session_key__gt=""),
                name="unique_like_per_session_per_image",
            ),
        ]

    def __str__(self):
        if self.user:
            return f"{self.user.username} liked #{self.image_id}"
        return f"Session liked #{self.image_id}"


class SiteVisit(models.Model):
    session_key = models.CharField(max_length=40)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (("session_key", "date"),)

    def __str__(self):
        return f"{self.session_key} - {self.date}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.subject}"

    def mark_as_read(self):
        """Mark message as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])

    def mark_as_replied(self):
        """Mark message as replied."""
        self.replied = True
        self.replied_at = timezone.now()
        self.save(update_fields=['replied', 'replied_at'])