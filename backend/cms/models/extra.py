"""
Integreat extras are extended features beyond pages and
events that are usually provided by foreign services.
"""
from django.db import models
from django.utils import timezone

from .region import Region
from .extra_template import ExtraTemplate


class Extra(models.Model):
    """
    An extra (addon) is activated per region. For each extra,
    a template exists which can be used during activation.
    """
    region = models.ForeignKey(Region, related_name='extras', on_delete=models.CASCADE)
    template = models.ForeignKey(ExtraTemplate, related_name='extras', on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def slug(self):
        # pylint: disable=E1101
        return self.template.slug

    @property
    def name(self):
        return self.template.name

    @property
    def thumbnail(self):
        # pylint: disable=E1101
        return self.template.thumbnail

    @property
    def url(self):
        # pylint: disable=E1101
        if self.template.use_postal_code == self.template.POSTAL_GET:
            return self.template.url + self.region.postal_code
        return self.template.url

    @property
    def post_data(self):
        # pylint: disable=E1101
        post_data = self.template.post_data
        if self.template.use_postal_code == self.template.POSTAL_POST:
            post_data.update({'search-plz': self.region.postal_code})
        return post_data

    # pylint: disable=R0903
    class Meta:
        unique_together = (('region', 'template', ), )
        default_permissions = ()
        permissions = (
            ('manage_extras', 'Can manage extras'),
        )
