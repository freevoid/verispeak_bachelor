from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseForbidden

from functools import wraps

from misc import json

SUCCESS_CODE = 0
DEFAULT_ERROR_CODE = -1

def json_response(code, message=''):
    return HttpResponse(json.dumps({"result":code, "message":message}), mimetype='application/javascript')

def api_ok(message=''):
    return json_response(code=SUCCESS_CODE, message=message)

def api_error(message='', error_code=1):
    return json_response(code=error_code, message=message)

def api_exception(exception):
    error_code = getattr(exception, 'code', DEFAULT_ERROR_CODE)
    is_json = getattr(exception, 'is_json', False)
    if is_json:
        message = exception.json_serializable()
    else:
        message = unicode(exception)
    return api_error(message, error_code)

def api_enabled(post_only=False):
    def decorator(view):
        def enabler(request, *args, **kwargs):
            try:
                retval = view(request, *args, **kwargs)
                if isinstance(retval, basestring):
                    return api_ok(retval)
                elif hasattr(retval, 'items'):
                    return api_ok(json.dumps(retval))
                else:
                    raise ValueError("Expected dict-like or string, got '%s'" % type(retval))

            except BaseException, e:
                return api_exception(e)

        if post_only:
            @wraps(view)
            def _wrapper(request, *args, **kwargs):
                if request.method == 'GET':
                    return view(request, *args, **kwargs)
                else:
                    return enabler(request, *args, **kwargs)
            return _wrapper
        else:
            return wraps(view)(enabler)
    return decorator

