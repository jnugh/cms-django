from django.http import JsonResponse, HttpResponse, HttpRequest

from federation import organiser
from federation.models import CMSCache
from federation.crypto_tools import derive_id_from_public_key

def cms_ids(request: HttpRequest):
    """
    :param request:
    :return: a JSON-response containing all region-ids in the cms
    """
    response_list = [
        cmsCacheEntry.id for cmsCacheEntry in CMSCache.objects.filter(share_with_others=True)
    ] + [organiser.get_id()]
    return JsonResponse(response_list, safe=False)

def cms_domain(request):
    pass

def cms_data(request: HttpRequest, cms_id: str):
    """
    :param request:
    :param cms_id: The id of the cms which data is requested
    :return: a JSON-response containing name, domain and public key of the cms specified by cms_id
    """
    if cms_id == organiser.get_id():
        response_dict = {
            "name": organiser.get_name(),
            "domain": organiser.get_domain(),
            "public_key": organiser.get_public_key()
        }
    else:
        response_cms = CMSCache.objects.get(id=cms_id)
        response_dict = {
            "name": response_cms.name,
            "domain": response_cms.domain,
            "public_key": response_cms.public_key
        }
    return JsonResponse(response_dict, safe=False)

def receive_offer(request: HttpRequest):
    public_key: str = request.GET["public_key"]
    cms_new = CMSCache(
        id=derive_id_from_public_key(public_key),
        name=request.GET["name"],
        domain=request.GET["domain"],
        public_key=public_key
    )
    cms_new.save()
    return HttpResponse()
