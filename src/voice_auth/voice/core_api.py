from django.conf import settings

import logging

from misc.snippets import log_exceptions
from models import VerificationProcess, SpeakerModel, UniversalBackgroundModel, LLRVerificator

from exceptions import NeedMoreDataError
from core import load_pickled_file, score

def verificate(target_session, verificator):
    verificator.null_estimator.model_file.open('r')
    null_model = load_pickled_file(verificator.null_estimator.model_file)

    verificator.alternative_estimator.model_file.open('r')
    alternative_model = load_pickled_file(verificator.alternative_estimator.model_file)

    target_utterances = target_session\
            .uploadedutterance_set.filter(is_trash=False)

    utterance_files = (u.utterance_file.path for u in target_utterances)
    scr = score(null_model, alternative_model, utterance_files)
    result = scr > verificator.treshhold
    return result, scr

@log_exceptions
def verification(verification_process_id, speaker_model_id):
    logging.info("Verification process: %s; Speaker model: %s", verification_process_id, speaker_model_id)

    try:
        verification_process = VerificationProcess.objects.get(id=verification_process_id)
    except VerificationProcess.DoesNotExist:
        logging.error("Wrong arguments to verification: no such VerificationProcess (id=%s)" % verification_process_id)
        return # fail silently

    try:
        speaker_model = SpeakerModel.objects.get(id=speaker_model_id)
    except SpeakerModel.DoesNotExist:
        verification_process.transition(verification_process.FAILED)
        return

    try:
        verificator = speaker_model.llr_verificator
    except:
        try:
            ubm = UniversalBackgroundModel.objects.latest()
        except:
            logging.error("Can't determine verificator for speaker (UBM not found)")
            verification_process.transition(verification_process.FAILED)
            return
        else:
            verificator = LLRVerificator.objects.create(null_estimator=speaker_model,
                    alternative_estimator=ubm,
                    treshhold=settings.GLOBAL_LLR_TRESHHOLD)

    # for now we have verificator and link to all uploaded utterances,
    # so we can verificate them
    try:
        result, score = verificate(verification_process.target_session,
                verificator)
    except NeedMoreDataError:
        logging.info("Need more data")
        verification_process.transition(verification_process.WAIT_FOR_DATA)
    except BaseException, e:
        logging.error(u"Exception raised during scoring: %s", e)
        verification_process.transition(verification_process.FAILED)
    else:
        logging.info("Verification finished! Result: %s", result)
        verification_process.verified_by = verificator
        verification_process.verification_score = score
        verification_process.verification_result = result
        # XXX defer save() to state transition?
        verification_process.target_session.authentic = True
        verification_process.target_session.save()
        verification_process.transition(verification_process.VERIFIED)

@log_exceptions
def learning(*args, **kwargs):
    print "Learning", args, kwargs

