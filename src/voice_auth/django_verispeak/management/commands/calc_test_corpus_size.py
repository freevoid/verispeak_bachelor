from django.core.management.base import BaseCommand
from django.conf import settings

from itertools import imap

from verispeak import wave
from django_verispeak.models import RecordSessionMeta

class Command(BaseCommand):
    help = ('Calculates length in seconds of all uploaded utterances from record sessions with meta data')
    requires_model_validation = True
    separator = '='*80

    def handle(self, **options):
        overall_timelength = 0
        overall_count = 0
        for test_session_meta in RecordSessionMeta.objects.all():
            def timelength_from_filepath(filepath):
                return wave.Wave(filepath).timelength
            current_timelength = sum(imap(timelength_from_filepath,
                    test_session_meta.record_session.utterance_filepath_iterator()))
            current_count = test_session_meta.record_session.uploadedutterance_set.count()
        
            overall_timelength += current_timelength
            overall_count += current_count
       
            self.printout_test_session_info(test_session_meta, current_count, current_timelength)
 
        print "Overall timelength:", overall_timelength
        print "Overall utterance count:", overall_count
        print "Average timelength: %.2f" % (overall_timelength / overall_count)

    def printout_test_session_info(self, session_meta, count, timelength):
        print self.separator
        print "Session id:",  session_meta.record_session.id
        print "Description:", session_meta.description
        print "Average timelength:", "%.2f" % (timelength / count)
        print self.separator


