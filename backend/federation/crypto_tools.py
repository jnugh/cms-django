from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import urlsafe_b64encode, urlsafe_b64decode

def generate_private_key() -> str:
    key_pair = RSA.generate(2048, Random.new().read)
    priv_key_string = key_pair.exportKey('PEM').decode()
    return priv_key_string

def derive_public_key_from_private_key(private_key_string: str) -> str:
    return RSA.importKey(private_key_string).publickey().exportKey('PEM').decode()

def derive_id_from_public_key(public_key_string: str) -> str:
    digest = SHA256.new()
    digest.update(public_key_string.encode())
    return digest.hexdigest()[:20]

def sign_message(message: str, private_key_string: str) -> str:
    private_key = RSA.import_key(private_key_string)
    signer = PKCS1_v1_5.new(private_key)
    digest = SHA256.new()
    digest.update(message.encode())
    signature_bytes = signer.sign(digest)
    return urlsafe_b64encode(signature_bytes).decode()

def verify_signature(message: str, signature: str, public_key_string: str) -> bool:
    signature_bytes = urlsafe_b64decode(signature.encode())
    public_key = RSA.importKey(public_key_string.encode())
    signer = PKCS1_v1_5.new(public_key)
    digest = SHA256.new()
    digest.update(message.encode())
    return signer.verify(digest, signature_bytes)
