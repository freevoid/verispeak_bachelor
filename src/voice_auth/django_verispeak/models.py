from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.db import models
from django.core import exceptions

import logging
import os.path
import datetime
import time

from state_machine.models import StateMachine
from misc.signature import sign_string
from misc.ip import ip_wrapper_property
from misc.flatten import flatiter
from misc import json

class Speaker(User):
    """
    """
    class Meta:
        proxy = True
        verbose_name = _("Speaker")
        verbose_name_plural = _("Speakers")

    def get_active_model(self):
        return SpeakerModel.objects.get(speaker=self,
                is_active=True)

class RecordSession(models.Model):
    class Meta:
        get_latest_by = 'created_time'
        verbose_name = _("Record session")
        verbose_name_plural = _("Record sessions")


    session_id = models.CharField(max_length=32, unique=True, verbose_name=_('session id'))
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('created time'))
    target_speaker = models.ForeignKey(Speaker, null=True, verbose_name=_('target speaker'))
    authentic = models.NullBooleanField(blank=True, null=True, verbose_name=_('authentic'))

    remote_ip = models.IntegerField(verbose_name=_('remote ip'))
    remote_ip_dotted_quad = ip_wrapper_property('remote_ip')

    @staticmethod
    def generate_session_id(request, **extra_data):
        stamp = str(time.time())
        session_id = sign_string('\n'.join([request.META['REMOTE_ADDR'],
            stamp,
            smart_str(extra_data)]))
        return session_id

    @property
    def utterance_count(self):
        return self.uploadedutterance_set.count()

    def utterance_filepath_iterator(self):
        media_root = settings.MEDIA_ROOT
        return (os.path.join(media_root, filename) for filename in flatiter(self.uploadedutterance_set\
                .filter(is_trash=False)\
                .values_list('utterance_file')))


    def __unicode__(self):
        return u'%d %s - %s - %s' % (self.pk, self.created_time.strftime('%d.%m.%Y %H:%M:%S'),
                self.target_speaker,
                self.utterance_count)

class SpeakerModel(models.Model):
    class Meta:
        get_latest_by = 'learning_process__finish_time'
        verbose_name = _('Speaker model')
        verbose_name_plural = _('Speaker models')

    MODELS_PATH = 'speaker_models'

    model_file = models.FileField(upload_to=MODELS_PATH, verbose_name=_('model file'))
    speaker = models.ForeignKey(Speaker, verbose_name=_('speaker'))
    is_active = models.BooleanField(default=False, verbose_name=_('is active'))

    def _set_active(self, active):
        if self.is_active != active:
            if active:
                old_active = SpeakerModel.objects.get(speaker=self.speaker, is_active=active)
                old_active.is_active = False
                self.is_active = True
                return old_active
            else:
                self.is_active = active
                return self

    def set_active(self, active):
        old = self._set_active(active)
        if old != self:
            old.save()
        self.save()
    def get_active(self):
        return self.is_active
    active_prop = property(get_active, set_active)

    def save(self, *args, **kwargs):
        '''
        if self.is_active:
            old_active = SpeakerModel.objects.get(speaker=self.speaker, is_active=True)
            if self != old_active:
                old_active.is_active = False
                old_active.save()
        '''
        if not self.model_file and not self.id:
            self.model_file.name = '.'
            super(SpeakerModel, self).save(*args, **kwargs)
            assert self.id
            self.model_file.name = self.generate_model_filename()
        super(SpeakerModel, self).save(*args, **kwargs)

    def generate_model_filename(self):
        name = [self.MODELS_PATH, '/', '%04d' % self.pk, '_s%04d' % self.speaker.id]
        try:
            if self.learning_process:
                name.append('_e%04d' % self.learning_process.id)
        except LearningProcess.DoesNotExist:
            pass
        name.append('.gmm')
        return ''.join(name)

    def __unicode__(self):
        return u'%s %s [%s]' % (self.speaker, self.is_active, self.model_file.name)

class LearningProcess(StateMachine):

    class Meta:
        get_latest_by = 'start_time'
        verbose_name = _('Learning process')
        verbose_name_plural = _('Learning processes')

    WAIT_FOR_DATA = 'waiting_for_data'
    STARTED = 'started'
    FAILED = 'failed'
    INTERRUPTED = 'interrupted'
    FINISHED = 'finished'

    initial_state = WAIT_FOR_DATA

    states = ((WAIT_FOR_DATA, _('Waiting for speech data')),
            (STARTED, _('Processing..')),
            (FAILED, _('Learning failed')),
            (INTERRUPTED, _('Learning canceled')),
            (FINISHED, _('Learning finished')),
            )

    state_id = models.CharField(max_length=24, choices=states)
    #STATE_DISPLAY = dict(states)

    transition_table = {
            WAIT_FOR_DATA: (STARTED, INTERRUPTED, WAIT_FOR_DATA),
            STARTED: (FAILED, FINISHED, WAIT_FOR_DATA, INTERRUPTED),
            }

    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_('start time'))
    finish_time = models.DateTimeField(blank=True, null=True, verbose_name=_('finish time'))

    sample_sessions = models.ManyToManyField(RecordSession, verbose_name=_('sample sessions'))

    retrain_model = models.ForeignKey(SpeakerModel, blank=True, null=True, verbose_name=_('retrain model'))
    result_model = models.OneToOneField(SpeakerModel, related_name='learning_process', blank=True, null=True, verbose_name=_('result model'))

    def sample_sessions_count(self):
        return self.sample_sessions.count()

    def sample_filepath_iterator(self):
        media_root = settings.MEDIA_ROOT
        return (os.path.join(media_root, filename) for filename in flatiter(s.uploadedutterance_set\
                .filter(is_trash=False)\
                .values_list('utterance_file') for s in self.sample_sessions.all()))

class UniversalBackgroundModel(models.Model):
    model_file = models.FileField(upload_to='ubm', verbose_name=_('model file'))
    created_time = models.DateTimeField(auto_now_add=True, verbose_name=_('created time'))

    class Meta:
        get_latest_by = 'created_time'
        verbose_name = _('Universal background model')
        verbose_name_plural = _('Universal background models')

    def __unicode__(self):
        return u"[%s %s]" % (self.pk, self.model_file.name)

class UploadedUtterance(models.Model):
    class Meta:
        get_latest_by = 'uploaded_date'
        verbose_name = _('Uploaded utterance')
        verbose_name_plural = _('Uploaded utterances')

    def get_filename(instance, filename=None):
        now = datetime.datetime.now()
        stamp = now.strftime("%H%M%S%f")
        if not instance.session or not instance.session.id:
            raise ValueError("Need a session to be set to determine upload path")
        base_dir = settings.RECORDING_SESSION_DIR
        return '%s/%s/%s.wav' % (base_dir, instance.session.id, stamp)

    utterance_file = models.FileField(upload_to=get_filename, verbose_name=_('utterance file'))
    uploaded_date = models.DateTimeField(auto_now_add=True, verbose_name=_('uploaded date'))
    is_trash = models.BooleanField(default=False, verbose_name=_('is trash'))
    
    session = models.ForeignKey(RecordSession, verbose_name=_('session'))

    @staticmethod
    def save_uploaded_utterance(request, uploaded_file, record_session):
        def save_uploaded_file(uploaded_file, path):
            f = open(path, 'wb')
            for chunk in uploaded_file.chunks(1024*20):
                f.write(chunk)
            f.close()

        ip_dotted_quad = request.META['REMOTE_ADDR']
        logging.info("Saving new utterance from %s: name='%s', size=%s",
                ip_dotted_quad, uploaded_file.name, uploaded_file.size)
        utterance = UploadedUtterance()
        utterance.session=record_session

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

class LLRVerificator(models.Model):
    class Meta:
        verbose_name = _("Verificator")
        verbose_name_plural = _("Verificators")
    treshhold = models.FloatField(verbose_name=_("entry threshold"))
    null_estimator = models.OneToOneField(SpeakerModel, verbose_name=_("null estimator"), related_name='llr_verificator')
    alternative_estimator = models.ForeignKey(UniversalBackgroundModel, verbose_name=_("alternative estimator"), blank=True)
    
    def save(self, *args, **kwargs):
        # if alternative estimator was not set, trying to set most recent one
        if self.alternative_estimator is None:
            self.alternative_estimator = UniversalBackgroundModel.objects.latest()
        super(LLRVerificator, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s %s %s" % (self.pk, self.null_estimator, self.alternative_estimator)

class VerificationProcess(StateMachine):
    class Meta:
        verbose_name = _("Verification process")
        verbose_name_plural = _("Verification processes")
        get_latest_by = 'start_time'

    WAIT_FOR_DATA = 'waiting_for_data'
    STARTED = 'started'
    CANCELED = 'canceled'
    VERIFIED = 'verified'
    FAILED = 'failed'

    initial_state = WAIT_FOR_DATA

    states = ((WAIT_FOR_DATA, _('Waiting for speech data')),
            (STARTED, _('Processing..')),
            (CANCELED, _('Verification has been canceled')),
            (VERIFIED, _('Verification finished')),
            (FAILED, _('Error occured during verification'))
            )

    state_id = models.CharField(max_length=24, choices=states, verbose_name=_('state'))
    #STATE_DISPLAY = dict(states)

    transition_table = {
            WAIT_FOR_DATA: (STARTED, CANCELED, WAIT_FOR_DATA),
            STARTED: (VERIFIED, FAILED, WAIT_FOR_DATA, STARTED),
            }

    start_time = models.DateTimeField(auto_now_add=True, verbose_name=_('start time'))
    target_session = models.ForeignKey(RecordSession, verbose_name=_('target session'))
    finish_time = models.DateTimeField(null=True, verbose_name=_('finish time'))
    verification_result = models.NullBooleanField(blank=True, null=True, verbose_name=_('verification result'))
    verification_score = models.FloatField(blank=True, null=True, verbose_name=_('verification score'))
    verificated_by = models.ForeignKey(LLRVerificator, blank=True, null=True, verbose_name=_('verificated by'))

class RecordSessionMeta(models.Model):
    class Meta:
        verbose_name = _("Record session meta data")
        verbose_name_plural = _("Record sessions meta data")

    record_session = models.OneToOneField(RecordSession)
    gender = models.CharField(max_length=1, default='M',
            verbose_name=_('gender'),
            choices=(('M', _('Male')), ('F', _('Female'))))
    prompt = models.CharField(max_length=256,
            verbose_name=_('prompt'), blank=True)
    description = models.CharField(max_length=512, blank=True,
            verbose_name=_('description'))

class SingletonError(Exception):
    def __str__(self):
        return "Somehow there are more than one instance of singleton object in DB"
class SingletonConstraint(Exception):
    def __str__(self):
        return "Can't create more than one instance of singleton object"

class SingletonManager(models.Manager):
    def get(self, *args, **kwargs):
        return super(SingletonManager, self).get()

    def create(self, *args, **kwargs):   
        self.ensure_can_create()
        return super(SingletonManager, self).create(*args, **kwargs)

    def ensure_can_create(self):
        try:
            self.get()
        except exceptions.ObjectDoesNotExist:
            pass
        except exceptions.MultipleObjectsReturned:
            raise SingletonError
        else:
            raise SingletonConstraint

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    objects = SingletonManager()
    
    @classmethod
    def get_instance(cls):
        return cls.objects.get()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.__class__.objects.ensure_can_create()
        return super(SingletonModel, self).save(*args, **kwargs)

class Settings(SingletonModel):
    class Meta:
        verbose_name = _("Settings")
        verbose_name_plural = verbose_name

    global_llr_threshold = models.FloatField(verbose_name=_("global entry threshold"))
    min_utterance_count_to_enroll = models.PositiveSmallIntegerField(verbose_name=_("minimal count of utterances needed to enroll"))
    speaker_model_parameters = models.CharField(max_length=256,
            verbose_name=_("parameters of speaker model instance"), default="{}")
    speaker_model_parameters_dict = json.json_converter("speaker_model_parameters")

    def __unicode__(self):
        return u"%s" % _("Settings")

