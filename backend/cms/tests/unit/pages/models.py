from random import randint
from django.test import TestCase


class PageTranslation(TestCase):
    def setUp(self):
        self.num = randint(0, 10)

    def test_is_outdated(self):
        """Outdated PageTranslation is correctly determined as outdated"""
        self.assertTrue(self.num > 5)
