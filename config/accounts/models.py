from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        NA = "N", "Prefer not to say"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
        default=Gender.NA,
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )

    def __str__(self):
        return self.user.username


# ✅ Create Profile ONLY ONCE (safe)
@receiver(post_save, sender=User, dispatch_uid="accounts_create_profile_once")
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
