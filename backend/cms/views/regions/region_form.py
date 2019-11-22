"""
Form for creating a region object
"""

import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from ...models import Region, Page, PageTranslation, LanguageTreeNode
from ..utils.slug_utils import generate_unique_slug

logger = logging.getLogger(__name__)


class RegionForm(forms.ModelForm):
    duplicated_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        empty_label=_("Do no import initial content"),
        required=False,
    )

    class Meta:
        model = Region
        fields = [
            'name',
            'slug',
            'events_enabled',
            'push_notifications_enabled',
            'push_notification_channels',
            'latitude',
            'longitude',
            'postal_code',
            'admin_mail',
            'statistics_enabled',
            'matomo_url',
            'matomo_token',
            'matomo_ssl_verify',
            'status',
            'page_permissions_enabled',
            'administrative_division',
            'aliases',
        ]

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):

        logger.info(
            'RegionForm saved with args %s, kwargs %s and cleaned data %s',
            args,
            kwargs,
            self.cleaned_data
        )

        # Only duplicate content if region is created and a region was selected
        duplicate_region = not self.instance.id and self.cleaned_data['duplicated_region']

        # Save region with the default method from ModelForm
        region = super(RegionForm, self).save(*args, **kwargs)

        if duplicate_region:
            source_region = self.cleaned_data['duplicated_region']
            logger.info(
                'Duplicate content of region %s to region %s',
                source_region,
                region
            )
            # Duplicate language tree
            duplicate_language_tree(source_region, region)
            # Duplicate pages
            duplicate_pages(source_region, region)
            # Duplicate media content
            duplicate_media(source_region, region)

        return region

    def clean_slug(self):
        return generate_unique_slug(self)


def duplicate_language_tree(source_region, target_region, source_parent_id=None, target_parent=None):
    """
    Function to duplicate the language tree of one region to another.

    Usage: duplicate_language_tree(source_region, target_region)

    This is a recursive function to walk the whole language tree. It starts at root level with the default parent None.
    The recursion is necessary because the new nodes need their correct (also duplicated) parent node.

    Args:
        :param source_region: The region from which the language tree should be duplicated
        :param target_region: The region to which the language tree should be added
        :param source_parent_id: The current parent node id of the recursion
        :param target_parent: The node of the target region which is the duplicate of the source parent node
    """

    # Iterate over all children of the current source parent, beginning with the root node
    for node in LanguageTreeNode.objects.filter(region=source_region, parent__id=source_parent_id).all():
        # Store the source node id for the next iteration
        source_node_id = node.pk
        # Change the region and parent to its new values
        node.region = target_region
        node.parent = target_parent
        # Delete the primary key to force an insert
        node.pk = None
        # Check if the resulting node is valid
        node.full_clean()
        # Save the duplicated node
        node.save()
        # Call the function recursively for all children of the current node
        duplicate_language_tree(source_region, target_region, source_node_id, node)


def duplicate_pages(source_region, target_region, source_parent_id=None, target_parent=None, level=0):
    """
    Function to duplicate all pages of one region to another.

    Usage: duplicate_pages(source_region, target_region)

    This is a recursive function to walk the whole page tree. It starts at root level with the default parent None.
    The recursion is necessary because the new pages need their correct (also duplicated) parent page.

    Args:
        :param source_region: The region from which the pages should be duplicated
        :param target_region: The region to which the pages should be added
        :param source_parent_id: The current parent page id of the recursion
        :param target_parent: The page of the target region which is the duplicate of the source parent page
        :param level: recursion level to get a pretty log output
    """

    logger.info(
        '%s Source parent %s started (target parent %s)',
        '|  ' * level + '├' + '─',
        source_parent_id,
        target_parent
    )

    # At first, get all pages from the source region with a specific parent page
    # As the parent will be None for the initial call, this returns all pages from the root level
    for target_page in Page.objects.filter(region=source_region, parent__id=source_parent_id).all():
        logger.info(
            '%s Source page %s started',
            '|  ' * (level + 1) + '├' + '─',
            target_page
        )
        # Store the source page id into a buffer (if we store the whole object instance instead of only the id,
        # it will also change when we change target_page, because both variables would reference the same object)
        source_page_id = target_page.pk
        # Set the parent of the new page to the previously created target parent
        target_page.parent = target_parent
        # Set the region of the new page to the target region
        target_page.region = target_region
        # Delete the primary key to duplicate the object instance instead of updating it
        target_page.pk = None
        # Check if the page is valid
        target_page.full_clean()
        # Save duplicated page
        target_page.save()
        # Clone all page translations of the source page
        for page_translation in PageTranslation.objects.filter(page__id=source_page_id):
            # Set the page of the source translation to the new page
            page_translation.page = target_page
            # Delete the primary key to duplicate the object instance instead of updating it
            page_translation.pk = None
            # Check if the page translation is valid
            page_translation.full_clean()
            # Save duplicated page translation
            page_translation.save()
            logger.info(
                '%s Page translation %s finished',
                '|  ' * (level + 3) + '├' + '─',
                page_translation
            )
        # Recursively call this function with the current pages as new parents
        duplicate_pages(source_region, target_region, source_page_id, target_page, level + 2)
        logger.info(
            '%s Source page %s finished (target page %s)',
            '|  ' * (level + 1) + '├' + '─',
            source_page_id,
            target_page
        )
    logger.info(
        '%s Source parent %s finished (target parent %s)',
        '|  ' * level + '├' + '─',
        source_parent_id,
        target_parent
    )


# pylint: disable=unused-argument
def duplicate_media(source_region, target_region):
    pass
    # TODO: implement duplication of all media files
