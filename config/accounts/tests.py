from django.test import TestCase
from django.contrib.auth.models import User


class ProfileSignalTests(TestCase):
    def test_profile_created_on_user_creation(self):
        u = User.objects.create_user(username="tuser", email="t@example.com", password="pass12345")
        # Accessing related `profile` should not raise
        self.assertIsNotNone(u.profile)
from django.test import TestCase

# Create your tests here.
