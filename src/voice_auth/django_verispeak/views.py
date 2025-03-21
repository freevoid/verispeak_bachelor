# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.db.models import Sum, Count
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from misc.snippets import allowed_methods, implicit_render, log_exception
from misc.ip import dotted_quad_to_num
from misc.amqp import register_queue, send_message

import logging

from exceptions import DoesNotExistError
from models import UploadedUtterance, RecordSession, Speaker,\
        SpeakerModel, VerificationProcess, LearningProcess,\
        RecordSessionMeta, Settings
from logic import api_enabled
from forms import VerificationRequestForm, EnrollmentRequestForm,\
        UploadConfirmForm, RetrainRequestForm

DEFAULT_APPLET_PARAMS = {
        'showLogo': 'no',
        'showPauseButton': 'no',
        'showTransport': 'no',
        'showVUMeter': 'no',
        'bevelSize': '0',
        'background': 'EEEEEE', 
        'uploadFileName': 'django_verispeak.wav',
        'requestStateChanges': 'yes',
        'stateChangeCallback': 'recordStateChanged',
        'requestTimeChanges': 'yes',
        'timeChangeCallback': 'recordTimeChanged',
        'timeChangeInterval': '100',
        'readyScript': 'recordAppletLoaded();',
        'packButtons': 'yes',
        'frameRate': 22000,
        'trimEnable': 'no',
        'maxRecordTime': 5
        }

APPLET_FILENAME = 'userfile'
DEFAULT_APPLET_WIDTH = 200
DEFAULT_APPLET_HEIGHT = 50

@allowed_methods('POST')
@never_cache
def upload_handler(request):
    try:
        uploaded_file = request.FILES['userfile']
        session_id = request.POST['session_id']
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

    except BaseException, e:
        log_exception()
        response = u'ERROR ' + unicode(e)
    else:
        response = 'SUCCESS'
    return HttpResponse(response, mimetype='text/plain')

@never_cache
@api_enabled()
def verification_state(request):
    session_id = request.GET.get('session_id')
    try:
        verification_process = VerificationProcess.objects.get(target_session__session_id=session_id)
    except VerificationProcess.DoesNotExist:
        raise DoesNotExistError("Verification process", session_id)
    
    state = verification_process.state_id
    if state == verification_process.VERIFIED:
        if verification_process.verification_result:
            state = 'verification_success'
            user = authenticate(username=request.GET.get('username'),
                    session_id=session_id, verification_process=verification_process)
            if user is not None and user.is_active:
                logging.info("Logging user `%s` in.." % user.username)
                login(request, user)
        else:
            state = 'verification_failed'
    return state

@implicit_render
@allowed_methods('GET')
def verification(request):
    #print "Verification", request.method, request.REQUEST
    remote_addr = request.META['REMOTE_ADDR']

    if request.method == 'GET':
        redirect_to = request.GET.get('redirect_to', settings.LOGIN_REDIRECT_URL)

        target_speaker = get_object_or_404(Speaker, username=request.REQUEST.get('username'))
        speaker_model = get_object_or_404(SpeakerModel,
                speaker__username=request.REQUEST.get('username'),
                is_active=True)

        session_id = RecordSession.generate_session_id(request, target_speaker=target_speaker.id)
        session, created = RecordSession.objects.get_or_create(
                session_id=session_id,
                remote_ip=dotted_quad_to_num(remote_addr),
                target_speaker=target_speaker
                )
        assert created

        verification_process = VerificationProcess.objects.create(target_session=session)

        applet_params = DEFAULT_APPLET_PARAMS.copy()
        applet_params['uploadURL'] = reverse('django_verispeak.views.upload_handler')
        applet_params['uploadFileName'] = session_id
        applet_params['maxRecordTime'] = '5.0'
        #applet_params['trimEnable'] = 'yes'
        return {'username': target_speaker.username,
                'session_id': session_id,
                'applet_params': applet_params,
                'redirect_to': redirect_to,
                'applet_width': DEFAULT_APPLET_WIDTH,
                'applet_height': DEFAULT_APPLET_HEIGHT,
                'login_url': settings.LOGIN_URL}

@api_enabled()
@allowed_methods('POST')
@transaction.autocommit
def verification_confirm(request):
    remote_addr = request.META['REMOTE_ADDR']
    form = VerificationRequestForm(request.REQUEST,
            remote_ip=dotted_quad_to_num(remote_addr))

    if form.is_valid(): # raises valid exceptions on errors
        # All validation done, so we need to verificate a session
        speaker_model = form.cleaned_data['speaker_model']
        verification_process = form.cleaned_data['verification_process']
        assert verification_process.target_session.utterance_count > 0, "Need at least 1 utterance to authenticate"
        verification_process.transition(VerificationProcess.STARTED)
        send_message("django_verispeak.verification",
                verification_process_id=verification_process.id,
                speaker_model_id=speaker_model.id)

        return _("Verification in progress")
    else:
        raise NotImplementedError

@api_enabled()
def verification_cancel(request):
    remote_addr = request.META['REMOTE_ADDR']
    form = VerificationRequestForm(request.REQUEST,
            remote_ip=dotted_quad_to_num(remote_addr))

    if form.is_valid():
        verification_process = form.cleaned_data['verification_process']
        verification_process.transition(verification_process.CANCELED)
    else:
        raise NotImplementedError

@never_cache
@api_enabled()
def enrollment_state(request):
    session_id = request.GET.get('session_id')
    try:
        enrollment_process = LearningProcess.objects.get(sample_sessions__session_id=session_id)
    except LearningProcess.DoesNotExist:
        raise DoesNotExistError("Learning process", session_id)
    
    state = enrollment_process.state_id
    return state

@implicit_render
@allowed_methods('GET')
def enrollment(request):
    #print "enrollment", request.method, request.REQUEST
    remote_addr = request.META['REMOTE_ADDR']

    if request.method == 'GET':
        redirect_to = request.GET.get('redirect_to', settings.LOGIN_REDIRECT_URL)
        target_speaker = get_object_or_404(Speaker, id=request.user.id)
        session_id = RecordSession.generate_session_id(request, target_speaker=target_speaker.id)
        session, created = RecordSession.objects.get_or_create(
                session_id=session_id,
                remote_ip=dotted_quad_to_num(remote_addr),
                target_speaker=target_speaker
        )
        assert created

        enrollment_process = LearningProcess.objects.create()
        enrollment_process.sample_sessions.add(session)

        applet_params = DEFAULT_APPLET_PARAMS.copy()
        applet_params['uploadURL'] = reverse('django_verispeak.views.upload_handler')
        applet_params['uploadFileName'] = session_id
        return {'username': target_speaker.username,
                'session_id': session_id,
                'applet_params': applet_params,
                'redirect_to': redirect_to,
                'applet_width': DEFAULT_APPLET_WIDTH,
                'applet_height': DEFAULT_APPLET_HEIGHT,
                'login_url': settings.LOGIN_URL}

@api_enabled()
@allowed_methods('POST')
@transaction.autocommit
def enrollment_confirm(request):
    remote_addr = request.META['REMOTE_ADDR']
    form = EnrollmentRequestForm(request.REQUEST,
            remote_ip=dotted_quad_to_num(remote_addr))

    if form.is_valid(): # raises valid exceptions on errors
        # All validation done, so we need to verificate a session
        dyn_settings = Settings.get_instance()
        enrollment_process = form.cleaned_data['enrollment_process']
        utterance_count = enrollment_process\
                .sample_sessions\
                    .aggregate(count=Count('uploadedutterance')).get('count')
        assert utterance_count > dyn_settings.min_utterance_count_to_enroll,\
                    _("Need at least %(count)d utterance to enroll") % {'count': utterance_count}

        target_speakers = enrollment_process.sample_sessions.values_list('target_speaker').distinct()
        assert target_speakers.count() == 1, _("More than one speaker tagged as target in sample sessions")

        target_speaker = target_speakers[0][0]
        assert request.user.id == target_speaker, _("Enrollment can be confirmed only by original person")
        enrollment_process.transition(LearningProcess.STARTED)
        send_message("django_verispeak.enrollment",
                enrollment_process_id=enrollment_process.id,
                target_speaker_id=target_speaker)

        return _("Enrollment in progress")
    else:
        raise NotImplementedError

@api_enabled()
def enrollment_cancel(request):
    remote_addr = request.META['REMOTE_ADDR']
    form = EnrollmentRequestForm(request.REQUEST,
            remote_ip=dotted_quad_to_num(remote_addr))
    if form.is_valid():
        enrollment_process = form.cleaned_data['enrollment_process']
        enrollment_process.transition(enrollment_process.INTERRUPTED)
        return 'canceled'
    else:
        raise NotImplementedError

@allowed_methods('GET')
@implicit_render
def upload(request):
    logging.info("Upload initialized")
    session_id = RecordSession.generate_session_id(request)
    confirm_form = UploadConfirmForm(remote_ip=None,
            initial={'session_id': session_id})
    applet_params = DEFAULT_APPLET_PARAMS.copy()
    applet_params['uploadFileName'] = session_id
    applet_params['uploadURL'] = reverse('django_verispeak.views.upload_handler')
    return {'applet_params': applet_params,
                'applet_width': DEFAULT_APPLET_WIDTH,
                'applet_height': DEFAULT_APPLET_HEIGHT,
                'session_id': session_id,
                'confirm_form': confirm_form}

@allowed_methods('POST')
@transaction.autocommit
def upload_confirm(request):
    remote_addr = request.META['REMOTE_ADDR']
    session_meta = RecordSessionMeta()
    confirm_form = UploadConfirmForm(request.POST,
            instance=session_meta,
            remote_ip=dotted_quad_to_num(remote_addr))

    if confirm_form.is_valid():
        confirm_form.save()
        return redirect('django_verispeak.index')
    raise TypeError

@api_enabled()
@allowed_methods('POST')
def upload_cancel(request):
    return ''

@login_required
@transaction.autocommit
@implicit_render
def retrain(request):
    speaker = get_object_or_404(Speaker, id=request.user.id)
    if request.method == 'POST':
        form = RetrainRequestForm(speaker, request.POST)
        if form.is_valid():
            enrollment_process = form.cleaned_data['enrollment_process']
            logging.info("Starting retrain process. Enrollment process: %s", enrollment_process.id)
            enrollment_process.save()
            enrollment_process.transition(enrollment_process.STARTED)
            send_message('django_verispeak.enrollment',
                    enrollment_process_id=enrollment_process.id,
                    target_speaker_id=speaker.id)
            speaker.message_set.create(message=_('Selected model has been successfully putted in queue for retraining'))
            return redirect('django_verispeak.index')
        else:
            return {'form': form}
    else:
        form = RetrainRequestForm(speaker)
        return {'form': form}

