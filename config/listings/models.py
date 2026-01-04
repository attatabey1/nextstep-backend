from django.db import models
from django.utils import timezone
from django.conf import settings


class Listing(models.Model):
    class ListingType(models.TextChoices):
        JOB = "JOB", "Job"
        SCHOLARSHIP = "SCHOLARSHIP", "Scholarship"
        COURSE = "COURSE", "Course"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"

    type = models.CharField(max_length=20, choices=ListingType.choices)
    title = models.CharField(max_length=255)

    image = models.ImageField(upload_to="listings/images/", blank=True, null=True)

    organization = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True)

    deadline = models.DateField(null=True, blank=True)
    remote = models.BooleanField(default=False)

    level = models.CharField(
        max_length=120,
        blank=True,
        help_text="Bachelor, Master, PhD, Short course, etc."
    )

    description = models.TextField(blank=True)

    apply_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)

    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-set status based on deadline (optional logic)
        if self.deadline:
            today = timezone.localdate()
            if self.deadline < today:
                self.status = self.Status.EXPIRED
            elif self.status == self.Status.EXPIRED:
                self.status = self.Status.ACTIVE

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ListingView(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="views")
    session_key = models.CharField(max_length=40)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (("listing", "session_key", "date"),)

    def __str__(self):
        return f"View: listing={self.listing_id} session={self.session_key} date={self.date}"


class SavedListing(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_listings"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "listing"),)

    def __str__(self):
        return f"{self.user_id} saved {self.listing_id}"
