# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_control

import datetime
import time

from misc.snippets import allowed_methods, implicit_render
from misc.ip import dotted_quad_to_num
from models import UploadedUtterance, RecordSession

DEFAULT_APPLET_PARAMS = {
        'showLogo': 'no',
        'showPauseButton': 'no',
        'uploadFileName': 'voice.wav',
        'requestStateChanges': 'yes',
        'stateChangeCallback': 'recordStateChanged',
        'readyScript': 'recordAppletLoaded();',
        'packButtons': 'yes',
        #'trimEnable': 'yes'
        }

APPLET_FILENAME = 'userfile'

@allowed_methods('POST')
@cache_control(private=True)
def upload_handler(request):
    try:
        uploaded_file = request.FILES['userfile']
        session_id = uploaded_file.name
        remote_addr = request.META['REMOTE_ADDR']
        # if ip is different from the initial, next statement
        # will raise an IntegrityError (and it's what we actually want)
        session, created = RecordSession.objects.get_or_create(
                session_id=session_id,
                remote_ip=dotted_quad_to_num(remote_addr)
                )

        UploadedUtterance.save_uploaded_utterance(
                request,
                uploaded_file,
                session
            )
    except BaseException as e:
        response = u'ERROR ' + unicode(e)
        print e.__class__, e
    else:
        response = 'SUCCESS'
    return HttpResponse(response, mimetype='text/plain')

@allowed_methods('GET')
@implicit_render
def upload(request):
    print "Upload", request.method, request.REQUEST
    applet_params = DEFAULT_APPLET_PARAMS.copy()
    applet_params['uploadURL'] = reverse('voice.views.upload_handler')
    applet_params['uploadFileName'] = RecordSession.generate_session_id(request)
    return {'applet_params': applet_params}

