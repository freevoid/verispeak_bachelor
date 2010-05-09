import os
import sys

sys.path.append('/home/devlish/workspace/diploma/src/voice_auth')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
