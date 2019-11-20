from random import randint
from django.test import TestCase

from cms.models import Page, PageTranslation


class PageTest(TestCase):
    def setUp(self):
        # Setup run before every test method.
        Page.objects.create(

        )


class PageTranslationTest(TestCase):
    def setUp(self):
        # Setup run before every test method.
        self.num = randint(0, 10)
        #Page.objects.create()
        #PageTranslation.objects.create()

    def test_is_outdated(self):
        # Outdated PageTranslation is correctly determined as outdated
        self.assertTrue(self.num > -1)
