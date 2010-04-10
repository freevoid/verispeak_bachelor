import os
import sys

sys.path.append('/home/devlish/workspace/diploma/src/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'voice_auth.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
