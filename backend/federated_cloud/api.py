from django.http import JsonResponse

from cms.models import Site
from federated_cloud.models import CMSCache


def cms_ids(request):
    response_list = [
        cmsCacheEntry.id for cmsCacheEntry in CMSCache.objects.filter(shareWithOthers=True)
    ]
    return JsonResponse(response_list, safe=False)


def cms_data(request, cms_id):
    response_cms = CMSCache.objects.get(id=cms_id)
    response_dict = {
        "name": response_cms.name,
        "domain": response_cms.domain,
        "public_key": response_cms.public_key
    }
    return JsonResponse(response_dict, safe=False)


def site_data(request):
    sites = Site.objects.all()
    response_list = [{
        "path": site.slug,
        "aliases": "",
        "latitude": site.latitude,
        "longitude": site.longitude,
        "postal_code": site.postal_code,
        "prefix": "",
        "name_without_prefix": site.name,
    } for site in sites]
    return JsonResponse(response_list, safe=False)

# todo: prefix, name_without_prefix and aliases
