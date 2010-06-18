from django.conf.urls.defaults import *

urlpatterns = patterns('voice_stats.views',
        (r'^(?P<username>[^/]+)/$', 'user_profile', {}, 'voice_stats.user_profile'),
    )

