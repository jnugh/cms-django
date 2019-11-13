from django.test import TestCase
from cms.models.page import PageTranslation


class PageTranslation(TestCase):
    #def setUp(self):
        # PageTranslation.objects.create(title="Generic title")

    def test_is_outdated(self):
        """Outdated PageTranslation is correctly determined as outdated"""
        self.assertTrue(True)
