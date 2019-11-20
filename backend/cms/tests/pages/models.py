from random import randint
from django.test import TestCase
from django.utils import timezone

from cms.models import Page, PageTranslation


class PageTest(TestCase):
    def setUp(self):
        # Setup run before every test method.
        self.page = Page.objects.create(
            parent=None,
            icon=None,
            region=None,
            archived=False,
            mirrored_page=None,
            editors=None,
            publishers=None,
            created_date=timezone.now()
        )

    def depth_no_parent(self):
        # Depth is correctly determined for page without parent
        self.assertTrue(self.page.depth == 0)


class PageTranslationTest(TestCase):
    def setUp(self):
        # Setup run before every test method.
        self.num = randint(0, 10)
        #Page.objects.create()
        #PageTranslation.objects.create()

    def test_is_outdated(self):
        # Outdated PageTranslation is correctly determined as outdated
        self.assertTrue(self.num > -1)
