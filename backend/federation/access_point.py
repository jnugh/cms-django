from django.http import JsonResponse, HttpResponse, HttpRequest

from federation import organiser
from federation.models import CMSCache
from federation.crypto_tools import derive_id_from_public_key
from federation.organiser import add_or_override_cms_cache, get_domain
from federation.request_sender import ask_for_cms_data


def cms_ids(request: HttpRequest):
    """
    :param request:
    :return: a JSON-response containing ids of all known cms (not the own id)
    """
    response_list = [
        cmsCacheEntry.id for cmsCacheEntry in CMSCache.objects.filter(share_with_others=True)
    ] + [organiser.get_id()]
    return JsonResponse(response_list, safe=False)

def cms_domain(request, cms_id):
    """
    Returns: If cms_id is present in the model CMSCache: the domain of this cms, null if not
    """
    cms = CMSCache.objects.get(id=cms_id)
    return HttpResponse(cms.domain)
    #todo: error handling: cms_id not present

def cms_data(request: HttpRequest):
    """
    :return: a JSON-response containing the own name and public key
    """
    response_dict = {
        "name": organiser.get_name(),
        "public_key": organiser.get_public_key()
    }
    return JsonResponse(response_dict, safe=False)

def receive_offer(request: HttpRequest):
    domain: str = request.GET["domain"]
    (name, public_key) = ask_for_cms_data(domain)
    add_or_override_cms_cache(name, domain, public_key)
    return HttpResponse()
