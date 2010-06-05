from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^verification/$', 'voice.views.verification'),
    (r'^verification/confirm/$', 'voice.views.verification_confirm'),
    (r'^verification/state/$', 'voice.views.verification_state'),
    (r'^verification/cancel/$', 'voice.views.verification_cancel'),

    (r'^enrollment/$', 'voice.views.enrollment'),
    (r'^enrollment/confirm/$', 'voice.views.enrollment_confirm'),
    (r'^enrollment/state/$', 'voice.views.enrollment_state'),
    (r'^enrollment/cancel/$', 'voice.views.enrollment_cancel'),

    (r'^upload/$', 'voice.views.upload'),
    (r'^upload/confirm/$', 'voice.views.upload_confirm'),
    (r'^upload/cancel/$', 'voice.views.upload_cancel'),

    (r'^upload/handler/$', 'voice.views.upload_handler'),
)
