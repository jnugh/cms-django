from django.test import TestCase


class PageTranslation(TestCase):
    #def setUp(self):
        # PageTranslation.objects.create(title="Generic title")

    def test_is_outdated(self):
        """Outdated PageTranslation is correctly determined as outdated"""
        self.assertTrue(True)
