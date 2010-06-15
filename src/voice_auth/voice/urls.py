from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template



urlpatterns = patterns('voice.views',
    (r'^$', direct_to_template, {'template': 'voice/index.html'}, "voice.index"),
    (r'^success/$', direct_to_template, {'template': 'voice/success.html'}, "voice.success"),
    (r'^fail/$', direct_to_template, {'template': 'voice/fail.html'}, "voice.fail"),
    (r'^verification/$', 'verification'),
    (r'^verification/confirm/$', 'verification_confirm'),
    (r'^verification/state/$', 'verification_state'),
    (r'^verification/cancel/$', 'verification_cancel'),

    (r'^enrollment/initial/$', direct_to_template, {'template': 'voice/enrollment_initial.html'}, "voice.enrollment.initial"),
    (r'^enrollment/$', 'enrollment'),
    (r'^enrollment/confirm/$', 'enrollment_confirm'),
    (r'^enrollment/state/$', 'enrollment_state'),
    (r'^enrollment/cancel/$', 'enrollment_cancel'),

    (r'^upload/$', 'upload'),
    (r'^upload/confirm/$', 'upload_confirm'),
    (r'^upload/cancel/$', 'upload_cancel'),

    (r'^upload/handler/$', 'upload_handler'),
)
