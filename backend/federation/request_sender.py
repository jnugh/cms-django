import json

import requests

from federation.organiser import get_domain

def ask_for_cms_ids(domain):
    """
    Asks the cms (specified by domain) for ids
    Returns: the list of ids
    """
    response = send_federation_request(domain, "cms-ids")
    response_list = json.loads(response)
    return response_list

def ask_for_cms_domain(domain, cms_id):
    response = send_federation_request(domain, "cms-domain/" + str(cms_id))
    return response

def ask_for_cms_data(domain):
    response = send_federation_request(domain, "cms-data")
    response_dict = json.loads(response)
    return (response_dict["name"], response_dict["public_key"])

def send_offer(domain: str):
    send_federation_request(domain, "offer", {"domain": get_domain()})

def send_federation_request(domain: str, tail: str, params=None) -> str:
    return requests.get("http://" + domain + "/federation/" + tail, params).text