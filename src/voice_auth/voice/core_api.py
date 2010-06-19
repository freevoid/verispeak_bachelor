from django.conf import settings

import logging
import datetime

from misc.snippets import log_exceptions, log_exception
from models import VerificationProcess, Speaker, SpeakerModel,\
        UniversalBackgroundModel, LLRVerificator, LearningProcess

from exceptions import NeedMoreDataError

from verispeak.util import load_pickled_file
from verispeak.api import score, enroll, retrain

def verificate(target_session, verificator):
    verificator.null_estimator.model_file.open('r')
    null_model = load_pickled_file(verificator.null_estimator.model_file)

    verificator.alternative_estimator.model_file.open('r')
    alternative_model = load_pickled_file(verificator.alternative_estimator.model_file)

    target_utterances = target_session\
            .uploadedutterance_set.filter(is_trash=False)

    utterance_files = (u.utterance_file.path for u in target_utterances)

    logging.info("Calculating LLR with models: NULL: %s; ALTERNATIVE: %s", null_model, alternative_model)
    scr = score(null_model, alternative_model, utterance_files)
    result = scr > verificator.treshhold
    return result, scr

def retrain_model(sample_files, speaker_model):
    speaker_model.model_file.open('r')
    model = load_pickled_file(speaker_model.model_file)
    retrained_model = retrain(model, sample_files)
    return retrained_model

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
        logging.info("Trying to verificate record session %s.." % verification_process.target_session.pk)
        result, score = verificate(verification_process.target_session,
                verificator)
    except NeedMoreDataError:
        logging.info("Need more data")
        verification_process.transition(verification_process.WAIT_FOR_DATA)
    except BaseException, e:
        logging.error(u"Exception raised during scoring: %s", e)
        verification_process.transition(verification_process.FAILED)
    else:
        logging.info("Verification finished! Result: %s, Score: %s", result, score)
        verification_process.verified_by = verificator
        verification_process.verification_score = score
        verification_process.verification_result = result
        # XXX defer save() to state transition?
        verification_process.target_session.authentic = result
        verification_process.target_session.save()

        verification_process.finish_time = datetime.datetime.now()
        verification_process.transition(verification_process.VERIFIED)

@log_exceptions
def enrollment(enrollment_process_id, target_speaker_id):
    logging.info("Learning, id=%d", enrollment_process_id)
    try:
        enrollment_process = LearningProcess.objects.get(id=enrollment_process_id)
    except LearningProcess.DoesNotExist:
        logging.error("No such LearningProcess: %s", enrollment_process_id)
        return

    try:
        target_speaker = Speaker.objects.get(id=target_speaker_id)
    except Speaker.DoesNotExist:
        logging.error("No such speaker in DB: %s", target_speaker_id)
        return

    sample_files = enrollment_process.sample_filepath_iterator()
    try:
        if enrollment_process.retrain_model is None:
            model = enroll(sample_files,
                model_classname=settings.SPEAKER_MODEL_CLASSNAME,
                model_parameters=settings.SPEAKER_MODEL_PARAMETERS)
        else:
            model = retrain_model(sample_files, enrollment_process.retrain_model)
    except NeedMoreDataError:
        logging.info("Need more data")
        enrollment_process.transition(enrollment_process.WAIT_FOR_DATA)
    except BaseException, e:
        log_exception(msg="Exception raised during enrollment:")
        enrollment_process.transition(enrollment_process.FAILED)
    else:
        logging.info("Learning stage finished!")
        logging.info(model)

        speaker_model = SpeakerModel(speaker=target_speaker)
        speaker_model.learning_process = enrollment_process
        #speaker_model.model_file.name = speaker_model.generate_model_filename()
        speaker_model.save()

        enrollment_process.result_model = speaker_model
        model.dump_to_file(speaker_model.model_file.path)

        enrollment_process.finish_time = datetime.datetime.now()
        enrollment_process.transition(enrollment_process.FINISHED)
 
        speaker_model.active_prop = True

