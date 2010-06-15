from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

urlpatterns = patterns('voice_stats.views',
        (r'^(?P<slug>\w+)/$', login_required(object_detail),
            {'queryset': User.objects, 'slug_field': 'username',
                'template_name': 'voice_stats/user_profile.html',
                'template_object_name': 'user'}, 'voice_stats.user_profile'),
    )

