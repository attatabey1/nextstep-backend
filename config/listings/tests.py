from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Listing, SavedListing


class SaveListingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="saver", password="pass12345")
        self.listing = Listing.objects.create(
            type=Listing.ListingType.JOB,
            title="Test Job",
            status=Listing.Status.ACTIVE,
        )

    def test_toggle_save_requires_login(self):
        resp = self.client.post(f"/en/listings/{self.listing.pk}/save/")
        # Redirect to login
        self.assertIn(resp.status_code, (302, 401, 403))

    def test_toggle_save_authenticated(self):
        # login then POST to language prefixed URL
        logged = self.client.login(username="saver", password="pass12345")
        self.assertTrue(logged)
        resp = self.client.post(f"/en/listings/{self.listing.pk}/save/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("saved", data)
from django.test import TestCase

# Create your tests here.
