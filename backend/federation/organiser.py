from backend import settings
from cms.models import Configuration
from federation.models import CMSCache
from federation.crypto_tools import derive_id_from_public_key, derive_public_key_from_private_key, generate_private_key

def activate_federation_feature():
    try:
        Configuration.objects.get(key="federation_private_key")
    except:
        Configuration(
            key="federation_private_key",
            value=generate_private_key()
        ).save()

def update_cms_data():
    """
    Asks all known CMSs for new cms_ids and asks for data of the new CMSs
    """
    cms_list = CMSCache.objects.all()
    cms_ids = [cms.id for cms in cms_list]
    for cms in cms_list:
        response_list = ask_for_cms_ids(cms.domain)
        for response in response_list:
            if response not in cms_ids:
                cms_ids.append(response)
                ask_for_cms_data(cms.domain, response)

def add_or_override_cms_cache(name, domain, public_key):
    pass

def get_id():
    return derive_id_from_public_key(get_public_key())

def get_name():
    return settings.FEDERATION["name"]

def get_domain():
    return settings.FEDERATION["domain"]

def get_public_key():
    return derive_public_key_from_private_key(get_private_key())

def get_private_key():
    return Configuration.objects.get(key="federation_private_key").value
