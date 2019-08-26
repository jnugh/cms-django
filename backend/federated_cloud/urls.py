from django.conf.urls import url

from federated_cloud import sharing, tests
from federated_cloud.settings import activate_federated_cloud_feature

urlpatterns = [
    url(r'^cms-ids/', sharing.cms_ids),
    url(r'^cms-data/(?P<cms_id>[0-9,a-z]+)/$', sharing.cms_data),
    url(r'^region-data/', sharing.region_data),
    url(r'^offer/', sharing.receive_offer),
    url(r'^test/', tests.test), #todo: remove test-stuff
    url(r'test-activate', tests.test_activate),
    url(r'test-send-offer', tests.test_send_offer),
    url(r'test-update', tests.test_update),
    url(r'test-ask', tests.test_ask)
]

activate_federated_cloud_feature()