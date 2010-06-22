from django.contrib.auth.models import User
import logging

class VoiceBackend:
    def authenticate(self, username=None, session_id=None, verification_process=None):
        logging.info("Low-level authentication of user `%s` by voice verification session id.." % username)
        if username is not None and verification_process is not None and session_id is not None:
            if verification_process.state_id == verification_process.VERIFIED and \
                    verification_process.verification_result == True and \
                    verification_process.target_session.session_id == session_id:
                user = self.get_user_by_username(username)
                if user and user.pk == verification_process.target_session.target_speaker.pk:
                    return user
        return None

    def get_user_by_username(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

