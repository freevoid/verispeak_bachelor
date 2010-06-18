from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from voice.models import Speaker, VerificationProcess, RecordSession
from misc.snippets import implicit_render

@login_required
@implicit_render
def user_profile(request, username):
    if (not request.user.is_superuser) and (request.user.username != username):
        return HttpResponseForbidden('Permission required')
    user = get_object_or_404(Speaker, username=username)
    verification_processes = VerificationProcess\
        .objects.filter(target_session__target_speaker=user)
        
    if verification_processes.count():
        last_verification_process = verification_processes.latest()
    else:
        last_verification_process = None
    return {'user': user,
            'verification_processes': verification_processes,
            'last_verification_process': last_verification_process}

