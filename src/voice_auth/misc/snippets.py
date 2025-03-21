# -*- coding: utf-8 -*-
from decimal import Decimal
from functools import wraps
import logging
import pprint
import sys
import traceback

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test, permission_required
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext

def raise_on_except(exception_class):
    from django.utils.encoding import smart_unicode
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseException as e:
                raise exception_class(smart_unicode(e))
        return wrapper
    return decorator

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain string with template name as first
    element and dict as second. The string will override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[0], output[1], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer

def implicit_render(func):
    splitted = func.__module__.rsplit('.', 2)
    if len(splitted) <= 2:
        app_name = splitted[0]
    elif len(splitted) > 2:
        app_name = splitted[1]
    template_name = '%s/%s.html' % (app_name, func.__name__)
    logging.debug("Setting implicit render to '%s' for function %s", template_name, func.__name__)
    return render_to(template_name)(func)

def allowed_methods(*methods):
    """
    Decorator for Django views that allows only specified HttpRequest methods to be processed.
    """
    def allower(func):
        @wraps(func)
        def wrapper(request, *args, **kw):
            if request.method in methods:
                return func(request, *args, **kw)
            return HttpResponseNotAllowed(methods)
        return wrapper
    return allower

def log_exception(msg=None):
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    error = pprint.pformat(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback))
    if msg:
        error = msg + error
    logging.error(error)
    
def log_exceptions(func):
    """
    Decorator that logging internal unexpected errors.
    """
    @wraps(func)
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except:
            log_exception()
            raise
    return wrapper

def error_message_on_exception(func):
    """
    Decorator for Django views that returns single variable 'error_message' if
    something went wrong (value is a BaseException instance).

    NOTE: Need to be under 'render_to' or similar decorator in decorator stack,
        because it returns dict and asserts that original func also returns dict.
        It also should be above log_exceptions and similar, because it didn't pass
        exception up.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            return {'error_message': e}
    return wrapper

def login_required(function=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
    
def listify(gen):
    "Convert a generator into a function which returns a list"
    def patched(*args, **kwargs):
        return list(gen(*args, **kwargs))
    return patched

def app_filter(appname, appfunc):
    """
    Check if appname is installed, import and return appfunc;
    If appname is not installed, bypassing.
    """
    if appname not in settings.INSTALLED_APPS:
        return lambda (fallback_func): fallback_func
    else:
        def decorator(fallback_func):
            modname, funcname = '.'.join((appname, appfunc)).rsplit('.', 1)
            module = __import__(modname, fromlist=[funcname])
            func = getattr(module, funcname)
            return func
        return decorator

import re
CANONICAL_NAME_SUB = re.compile(r'([a-z])([A-Z])'), r'\1_\2'
def get_canonical_name(klass):
    """
    Fast Example:
    >>> class SomeDjangoModel: pass
    >>> get_canonical_name(SomeDjangoModel)
    'some_django_model'
    """
    regexp, sub =  CANONICAL_NAME_SUB
    return regexp.sub(sub, klass.__name__)

def app_curry(app_name):
    """
    Returns decorator which provides 'app_name' argument to function
    """
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs.update({'app_name': app_name})
            return func(*args, **kwargs)
        return wrapper
    return deco

def object_edit(app_name, klass=None, add_message=u"Объект создан", edit_message=u'Изменения сохранены',
        canonical_name=None, form_klass=None, list_view=None):

    if form_klass is None:
        module = __import__("%s.forms" % app_name, fromlist=[klass.__name__ + 'Form'])
        form_klass = getattr(module, klass.__name__ + 'Form')

    if canonical_name is None:
        canonical_name = str(klass.__name__).lower()

    if list_view is None:
        list_view = '%s.views.%s_list' % (app_name, canonical_name)
    display_view = '%s.views.%s' % (app_name, canonical_name)

    def decorator(view):
        @wraps(view)
        def wrapper(request, id=None):
            context = view(request, id=id)
            if isinstance(context, tuple):
                deferred_actions, context = context
            else:
                deferred_actions = None

            if id is not None:
                object_ = get_object_or_404(klass, id=id)
                is_edit = True
            else:
                object_ = klass()
                is_edit = False

            if request.method == 'POST':
                form = form_klass(request.POST, instance=object_)
                if form.is_valid() and not context.get('has_errors'):
                    form.save()

                    if deferred_actions is not None:
                        map(lambda action: apply(action, (object_,)), deferred_actions)

                    if not is_edit:
                        request.user.message_set.create(message=add_message)
                        return HttpResponseRedirect(reverse(list_view))
                    else:
                        request.user.message_set.create(message=edit_message)
                        return HttpResponseRedirect(reverse(display_view, args=[id]))
            else:
                form = form_klass(instance=object_)
            
            context.update({'form': form, 'is_edit': is_edit})
            return context
        return wrapper
    return decorator

def permission_checker(login_url=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs.has_key('perm'):
                perm = kwargs.pop('perm')
                if perm == 'superuser':
                    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)(func)(*args, **kwargs)
                else:
                    return permission_required(perm, login_url=login_url)(func)(*args, **kwargs)
        return wrapper
    return decorator

def user_passes_test_with_403(test_func, login_url=None, fail_template='403.html'):
    """
    Decorator for views that checks that the user passes the given test.
    
    Anonymous users will be redirected to login_url, while users that fail
    the test will be given a 403 error.
    """
    if not login_url:
        from django.conf import settings
        login_url = settings.LOGIN_URL
    def _dec(view_func):
        def _checklogin(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            elif not request.user.is_authenticated():
                return HttpResponseRedirect('%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, quote(request.get_full_path())))
            else:
                resp = render_to_response(fail_template, context_instance=RequestContext(request))
                resp.status_code = 403
                return resp
        _checklogin.__doc__ = view_func.__doc__
        _checklogin.__dict__ = view_func.__dict__
        return _checklogin
    return _dec

def permission_required_with_403(perm, login_url=None, fail_template='403.html'):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page or rendering a 403 as necessary.
    """
    return user_passes_test_with_403(lambda u: u.has_perm(perm), login_url=login_url, fail_template=fail_template)

def dummy_init(klass):
    def set_attrs_call_super(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        return super(klass, self)
    klass.__init__ = set_attrs_call_super
    return klass

def autodiscover(cb_module_name, site_cls, registry_attr_name='_registry'):
    """
    Auto-discover INSTALLED_APPS cb_module_name.py modules and fail silently when
    not present. This forces an import on them to register any  neccessary bits.
    """

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's cb module.
        try:
            before_import_registry = copy.copy(getattr(site_cls, registry_attr_name))
            import_module('%s.%s' % (app, cb_module_name))
        except:
            setattr(site_cls, registry_attr_name, before_import_registry)

            # Decide whether to bubble up this error. If the app just
            # doesn't have a neccessary module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, cb_module_name):
                raise

