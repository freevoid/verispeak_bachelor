from django import forms
from django.utils.translation import ugettext_lazy as _

from models import RecordSession, Speaker, SpeakerModel,\
        VerificationProcess, LearningProcess, RecordSessionMeta
import exceptions

class RequestForm(forms.Form):
    session_id = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.remote_ip = kwargs.pop('remote_ip')
        super(RequestForm, self).__init__(*args, **kwargs)

    def _check_required(self, field_names, data):
        for f in field_names:
            if not data.get(f):
                raise exceptions.ArgumentRequiredError(f)

class VerificationRequestForm(RequestForm):
    username = forms.CharField(required=False)

    def clean(self):
        data = self.cleaned_data
        self._check_required(('session_id', 'username'), data)

        username = data['username']
        session_id = data['session_id']
        try:
            target_speaker = Speaker.objects.get(username=username)

            speaker_model = SpeakerModel.objects\
                    .filter(speaker__username=username,
                            is_active=True)\
                    .get()

            record_session = RecordSession.objects.get(
                session_id=session_id,
                remote_ip=self.remote_ip,
                target_speaker=target_speaker
                )

            verification_process = VerificationProcess.objects.get(
                    target_session=record_session)
        except Speaker.DoesNotExist:
            raise exceptions.TargetSpeakerDoesNotExistError(username)
        except SpeakerModel.DoesNotExist:
            raise exceptions.SpeakerModelDoesNotExistError(username)
        except RecordSession.DoesNotExist:
            raise exceptions.SessionDoesNotExistError(session_id)
        except VerificationProcess.DoesNotExist:
            raise exceptions.DoesNotExistError("Verification process",
                    session_id)

        data['speaker_model'] = speaker_model
        data['verification_process'] = verification_process

        return data

class EnrollmentRequestForm(RequestForm):
    def clean(self):
        data = self.cleaned_data
        self._check_required(('session_id',), data)

        session_id = data['session_id']
        try:
            record_session = RecordSession.objects.get(
                session_id=session_id,
                remote_ip=self.remote_ip,
                )

            enrollment_process = LearningProcess.objects.get(
                    sample_sessions__in=[record_session])
        except RecordSession.DoesNotExist:
            raise exceptions.SessionDoesNotExistError(session_id)
        except LearningProcess.DoesNotExist:
            raise exceptions.DoesNotExistError("Learning process",
                    session_id)

        data['enrollment_process'] = enrollment_process
        return data

class UploadConfirmForm(forms.ModelForm):
    class Meta:
        model = RecordSessionMeta
        exclude = ('record_session',)

    session_id = forms.CharField(widget=forms.HiddenInput)
    description = forms.CharField(label=_('Description'), required=False,
            widget=forms.Textarea(attrs={'rows':3, 'cols': 20}))

    def __init__(self, *args, **kwargs):
        self.remote_ip = kwargs.pop('remote_ip')
        super(UploadConfirmForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data

        session_id = data['session_id']
        try:
            record_session = RecordSession.objects.get(
                session_id=session_id,
                remote_ip=self.remote_ip,
                )
        except RecordSession.DoesNotExist:
            raise exceptions.SessionDoesNotExistError(session_id)

        data['record_session'] = record_session
        if self.instance:
            self.instance.record_session_id = record_session.id
        return data

from django.db.models import Q
class RetrainRequestForm(forms.Form):
    def __init__(self, speaker, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

        self.fields['speaker_model'] = forms.ModelChoiceField(
                label=_('Speaker models'),
                queryset=speaker.speakermodel_set)

        self.fields['record_sessions'] = forms.ModelMultipleChoiceField(
                label=_('Record sessions'),
                queryset=RecordSession.objects.filter(
                    Q(target_speaker__isnull=True) | Q(target_speaker__id=speaker.id)))

    def clean(self):
        data = self.cleaned_data
        speaker_model = data['speaker_model']
        record_sessions = data['record_sessions']

        enrollment_process = LearningProcess.objects.create(
                    retrain_model=speaker_model)

        enrollment_process.sample_sessions.add(*record_sessions)

        data['enrollment_process'] = enrollment_process
        return data

