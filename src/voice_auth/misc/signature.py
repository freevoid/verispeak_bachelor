from django.conf import settings
from django.utils.encoding import smart_str
import base64
import hashlib
import hmac

def sign_string(string_to_sign):
    secret_key = settings.SECRET_KEY
    hmac_sha1_hash = hmac.new(smart_str(secret_key), smart_str(string_to_sign), hashlib.sha1).digest()
    signature = base64.b64encode(hmac_sha1_hash)
    return signature

