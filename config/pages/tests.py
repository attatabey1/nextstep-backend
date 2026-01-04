from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import GalleryImage


class GalleryLikeTests(TestCase):
    def setUp(self):
        self.client = Client()
        img_file = SimpleUploadedFile("img.jpg", b"\x47\x49\x46\x38", content_type="image/jpeg")
        self.img = GalleryImage.objects.create(title="G", caption="c", image=img_file)

    def test_gallery_like_anonymous(self):
        # include language prefix used by i18n_patterns
        resp = self.client.post(f"/en/gallery/{self.img.pk}/like/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("likes", data)
from django.test import TestCase

# Create your tests here.
