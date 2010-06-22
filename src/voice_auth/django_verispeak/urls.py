from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf import settings

urlpatterns = patterns('django_verispeak.views',
    (r'^$', direct_to_template, {'template': 'django_verispeak/index.html'}, "django_verispeak.index"),
    (r'^success/$', direct_to_template, {'template': 'django_verispeak/success.html'}, "django_verispeak.success"),
    (r'^fail/$', direct_to_template, {'template': 'django_verispeak/fail.html'}, "django_verispeak.fail"),

    (r'^retrain/$', 'retrain'),

    (r'^verification/$', 'verification'),
    (r'^verification/confirm/$', 'verification_confirm'),
    (r'^verification/state/$', 'verification_state'),
    (r'^verification/cancel/$', 'verification_cancel'),

    (r'^enrollment/initial/$', direct_to_template,
        {'template': 'django_verispeak/enrollment_initial.html',
            'extra_context': {'registration_opened': settings.REGISTRATION_OPENED}},
        "django_verispeak.enrollment.initial"),
    (r'^enrollment/$', 'enrollment'),
    (r'^enrollment/confirm/$', 'enrollment_confirm'),
    (r'^enrollment/state/$', 'enrollment_state'),
    (r'^enrollment/cancel/$', 'enrollment_cancel'),

    (r'^upload/$', 'upload'),
    (r'^upload/confirm/$', 'upload_confirm'),
    (r'^upload/cancel/$', 'upload_cancel'),

    (r'^upload/handler/$', 'upload_handler'),
)
