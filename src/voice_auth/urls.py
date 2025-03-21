from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.contrib import admin
admin.autodiscover()

from misc import amqp
amqp.autodiscover()
amqp.setup_queues()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/voice/'}),
    (r'^voice/', include('django_verispeak.urls')),

    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                                    {'document_root': settings.MEDIA_ROOT}),)
    if hasattr(settings, 'ADMIN_MEDIA_ROOT'):
        urlpatterns += patterns('', url(r'^%s/(?P<path>.*)$' % settings.ADMIN_MEDIA_PREFIX.strip('/'),
            'django.views.static.serve', 
            {'document_root': settings.ADMIN_MEDIA_ROOT}),)

urlpatterns += patterns('django.contrib.auth.views',
        url(r'^accounts/login/', 'login', name='login'),
        url(r'^accounts/logout/', 'logout', {'template_name': 'django_verispeak/logout.html'}, name='logout'),
        (r'^accounts/$', redirect_to, {'url': '/accounts/login/'})
        )

from django.views.generic.create_update import create_object
from django.contrib.auth.forms import UserCreationForm
urlpatterns += patterns('',
        (r'^registration/', create_object,
            {'form_class': UserCreationForm, 'template_name': 'registration/registration.html'},
            'registration')
        )

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

urlpatterns += patterns('',
    (r'^users/', include('voice_stats.urls')),
    (r'^accounts/profile/$', login_required(lambda request: redirect('voice_stats.views.user_profile', username=request.user.username))),
    )


urlpatterns += patterns('',
    (r'^favicon\.ico$', redirect_to, {'url': '/media/img/favicon.ico'}),
    )

