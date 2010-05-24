from django import forms

from models import RecordSession, Speaker, SpeakerModel,\
        VerificationProcess
import exceptions

class VerificationRequestForm(forms.Form):
    session_id = forms.CharField(required=False)
    username = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.remote_ip = kwargs.pop('remote_ip')
        super(VerificationRequestForm, self).__init__(*args, **kwargs)

    def _check_required(self, field_names, data):
        for f in field_names:
            if not data.get(f):
                raise exceptions.ArgumentRequiredError(f)

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

