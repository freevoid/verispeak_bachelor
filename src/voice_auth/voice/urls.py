from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #(r'^upload_sound/', 'voice_auth.amf.gateway.upload_gateway'),
    (r'^upload/$', 'voice.views.upload'),
    (r'^upload/handler/$', 'voice.views.upload_handler'),
)
