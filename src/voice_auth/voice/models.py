from django.contrib.admin.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db import models

import datetime
import time

from state_machine.models import StateMachine
from misc.signature import sign_string

def ip_wrapper_property(ip_attr_name):
    import socket, struct
    def dotted_quad_to_num(ip):
        "convert decimal dotted quad string to long integer"
        return struct.unpack('L',socket.inet_aton(ip))[0]

    def num_to_dotted_quad(n):
        "convert long int to dotted quad string"
        return socket.inet_ntoa(struct.pack('L',n))

    def getter(self):
        return num_to_dotted_quad(getattr(self, ip_attr_name))

    def setter(self, dotted_quad):
        setattr(self, ip_attr_name,
                dotted_quad_to_num(dotted_quad))

    return property(getter, setter)

class Speaker(User):
    """
    """
    class Meta:
        proxy = True

class RecordSession(models.Model):
    session_id = models.CharField(max_length=32, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    target_speaker = models.ForeignKey(Speaker, null=True)

    @staticmethod
    def generate_session_id(request):
        now = datetime.datetime.now()
        #stamp = now.strftime("%H%M%S%f")
        stamp = str(time.time())
        session_id = sign_string('\n'.join([request.META['REMOTE_ADDR'],
            stamp]))
        return session_id

    def __unicode__(self):
        return u'%s - %s - %s' % (self.created_time.strftime('%d.%m.%Y %H:%M:%S'),
                self.target_speaker,
                self.uploadedutterance_set.count())

class LearningProcess(StateMachine):

    CREATED = 'waiting_for_data'
    STARTED = 'started'
    FAILED = 'failed'
    INTERRUPTED = 'interrupted'
    FINISHED = 'finished'

    states = ((CREATED, _('Waiting for speech data')),
            (STARTED, _('Processing..')),
            (FAILED, _('Learning failed')),
            (INTERRUPTED, _('Learning canceled')),
            (FINISHED, _('Learning finished')),
            )

    state = models.CharField(max_length=24, choices=states)
    #STATE_DISPLAY = dict(states)

    transition_table = {
            CREATED: (STARTED, INTERRUPTED, CREATED),
            STARTED: (FAILED, FINISHED, CREATED, INTERRUPTED),
            }

    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(blank=True, null=True)

    sample_sessions = models.ManyToManyField(RecordSession)

class SpeakerModel(models.Model):
    model_file = models.FileField(upload_to='speaker_models')
    speaker = models.ForeignKey(Speaker)
    learning_process = models.OneToOneField(LearningProcess)

class VerificationSession(RecordSession):
    verification_result = models.BooleanField()

class UploadedUtterance(models.Model):
    def get_filename(instance, filename=None):
        now = datetime.datetime.now()
        stamp = now.strftime("%H%M%S%f")
        if not instance.session or not instance.session.id:
            raise ValueError("Need a session to be set to determine upload path")
        base_dir = settings.RECORDING_SESSION_DIR
        return '%s/%s/%s.wav' % (base_dir, instance.session.id, stamp)

    utterance_file = models.FileField(upload_to=get_filename)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    uploader_ip = models.IntegerField()
    uploader_ip_dotted_quad = ip_wrapper_property('uploader_ip')
    
    session = models.ForeignKey(RecordSession)

    @staticmethod
    def save_uploaded_utterance(request, uploaded_file, record_session):
        def save_uploaded_file(uploaded_file, path):
            f = open(path, 'wb')
            for chunk in uploaded_file.chunks(1024*20):
                f.write(chunk)
            f.close()

        ip_dotted_quad = request.META['REMOTE_ADDR']
        print "Saving new utterance from %s: name='%s', size=%s" % (ip_dotted_quad, uploaded_file.name, uploaded_file.size)
        utterance = UploadedUtterance()
        utterance.session=record_session
        utterance.uploader_ip_dotted_quad = ip_dotted_quad

        filename = utterance.get_filename()
        utterance.utterance_file.name = filename
        abspath = utterance.utterance_file.path
        import os
        dirname = os.path.dirname(abspath)
        os.system('mkdir -p "%s"' % dirname)

        save_uploaded_file(uploaded_file, abspath)
        utterance.save()

    def __unicode__(self):
        return u'%s - %s' % (self.uploaded_date.strftime('%d.%m.%Y %H:%M:%S'),
                self.utterance_file.name)

class VerificationProcess(StateMachine):
    CREATED = 'waiting_for_data'
    STARTED = 'started'
    CANCELED = 'canceled'
    VERIFIED = 'verified'

    states = ((CREATED, _('Waiting for speech data')),
            (STARTED, _('Processing..')),
            (CANCELED, _('Verification has been canceled')),
            (VERIFIED, _('Verification finished')),
            )

    state = models.CharField(max_length=24, choices=states)
    #STATE_DISPLAY = dict(states)

    transition_table = {
            CREATED: (STARTED, CANCELED, CREATED),
            STARTED: (VERIFIED, STARTED),
            }

    start_time = models.DateTimeField(auto_now_add=True)
    target_session = models.ForeignKey(VerificationSession)
    finish_time = models.DateTimeField(null=True)
    verificated_by = models.ForeignKey(SpeakerModel)

