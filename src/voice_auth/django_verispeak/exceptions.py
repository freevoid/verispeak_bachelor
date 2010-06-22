from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str

from misc import json

class CodedException(BaseException):
    code = -1
    is_json = False
    message = ''
    
    def __str__(self):
        return smart_str(unicode(self))

    def __unicode__(self):
        if not self.is_json:
            return self.message
        else:
            return json.dumps(self.json_serializable())

class ArgumentRequiredError(CodedException):
    code = 1
    is_json = True

    def __init__(self, argument_name):
        self.argument_name = argument_name

    def json_serializable(self):
        return {'argument_name': self.argument_name}

class DoesNotExistError(CodedException):
    code = 2
    is_json = True

    def __init__(self, object_name, object_args):
        self.object_name = object_name
        self.object_args = object_args

    def json_serializable(self):
        return {'object_name': self.object_name,
                'object_args': self.object_args}

class TargetSpeakerDoesNotExistError(DoesNotExistError):
    code = 3
    def __init__(self, username):
        super(TargetSpeakerDoesNotExistError, self).__init__(
                object_name=_('Target speaker'),
                object_args=(username,))

class SpeakerModelDoesNotExistError(DoesNotExistError):
    code = 4
    def __init__(self, username):
        super(SpeakerModelDoesNotExistError, self).__init__(
                object_name=_('Speaker model'),
                object_args=(username,))

class SessionDoesNotExistError(DoesNotExistError):
    code = 5
    def __init__(self, session_id):
        super(SessionDoesNotExistError, self).__init__(
                object_name=_('Record session'),
                object_args=(session_id,))

class NeedMoreDataError(CodedException):
    code = 6
    message = _("Need more speech to verificate")

