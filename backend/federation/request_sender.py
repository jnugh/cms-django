import json

from federation.models import CMSCache
from federation.organiser import get_name, get_domain, get_public_key, get_id

def ask_for_cms_ids(domain):
    response = send_federation_request(domain, "cms-ids")
    response_list = json.loads(response)
    return response_list

def ask_for_cms_domain(domain, cms_id):
    pass

def ask_for_cms_data(domain):
    if cms_id != get_id():
        response = send_federation_request(domain, "cms-data/" + str(cms_id))
        response_dict = json.loads(response)
        response_cms = CMSCache(
            id=cms_id,
            name=response_dict["name"],
            domain=response_dict["domain"],
            public_key=response_dict["public_key"],
        )
        response_cms.save()

def send_offer(domain: str):
    send_federation_request(domain, "offer", {"name": get_name(), "domain": get_domain(), "public_key": get_public_key()})

def send_federation_request(domain: str, tail: str, params=None) -> str:
    return requests.get("http://" + domain + "/federation/" + tail, params).text