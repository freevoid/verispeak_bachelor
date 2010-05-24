from datetime import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise
from django.utils.simplejson import dumps as sj_dumps, loads
from django.utils.translation import force_unicode

class LazyJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        else:
            return super(LazyJSONEncoder, self).default(o)
            
def dumps(d):
    return sj_dumps(d, cls=LazyJSONEncoder)

def parse_datetime(str):
    return datetime.strptime(str, "%Y-%m-%d %H:%M:%S")

def json_converter(attr_name):
    """
    Returns property object which wraps given attr_name with json load/dump
    """
    
    def getter(instance):
        json_str = getattr(instance, attr_name)
        return loads(json_str) if json_str is not None else None

    def setter(instance, dict_):
        setattr(instance, attr_name, dumps(dict_))
    
    return property(getter, setter)
