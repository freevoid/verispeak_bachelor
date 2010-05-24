from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from misc import amqp
amqp.autodiscover()
amqp.setup_queues()

urlpatterns = patterns('',
    #(r'^upload_sound/', 'voice_auth.amf.gateway.upload_gateway'),
    (r'^voice/', include('voice.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                                    {'document_root': settings.MEDIA_ROOT}),)

