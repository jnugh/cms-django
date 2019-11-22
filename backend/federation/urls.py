from django.conf.urls import url

from federation import access_point, tests
from federation.organiser import activate_federation_feature

urlpatterns = [
    url(r'^cms-ids/', access_point.cms_ids),
    url(r'cms_domain/(?P<cms_id>[0-9,a-z]+)/$', access_point.cms_domain),
    url(r'^cms-data/', access_point.cms_data),
    url(r'^offer/', access_point.receive_offer),
    url(r'^test/', tests.test), #todo: remove test-stuff
    url(r'test-activate', tests.test_activate),
    url(r'test-send-offer', tests.test_send_offer),
    url(r'test-update', tests.test_update),
    url(r'test-ask', tests.test_ask)
]

activate_federation_feature()