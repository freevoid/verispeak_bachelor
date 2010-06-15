from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from voice.models import Speaker, VerificationProcess, RecordSession
from misc.snippets import implicit_render

@login_required
@implicit_render
def user_profile(request, username):
    user = get_object_or_404(Speaker, username=username)
    last_verification_process = VerificationProcess\
        .objects.filter(target_session__target_speaker=user)\
        .latest()
    return {'user': user, 'last_verification_process': last_verification_process}

