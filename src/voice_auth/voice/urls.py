from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^verification/$', 'voice.views.verification'),
    (r'^verification/confirm/$', 'voice.views.verification_confirm'),
    (r'^verification/state/$', 'voice.views.verification_state'),
    (r'^verification/cancel/$', 'voice.views.verification_cancel'),
    (r'^upload/$', 'voice.views.upload'),
    (r'^upload/handler/$', 'voice.views.upload_handler'),
)
