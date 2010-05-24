from django.conf import settings
from django.utils.encoding import smart_str
from urllib import urlencode
import base64
import hashlib
import hmac

def canonicalized_query_string(params):
    if isinstance(params, dict):
        params = params.items()
    params.sort(lambda x, y: cmp(str(x[0]), str(y[0])))
    return urlencode(params)

def sign_dict(dict_to_sign):
    return sign_string(canonicalized_query_string(dict_to_sign))

def sign_string(string_to_sign):
    secret_key = settings.SECRET_KEY
    hmac_sha1_hash = hmac.new(smart_str(secret_key), smart_str(string_to_sign), hashlib.sha1).digest()
    signature = base64.b64encode(hmac_sha1_hash)
    return signature

