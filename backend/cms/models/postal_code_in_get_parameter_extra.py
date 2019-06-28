from cms.models.extra import Extra


class PostalCodeInGetParameterExtra(Extra):

    def url(self):
        return self.template.url + self.site.postal_code

    class Meta:
        default_permissions = ()
