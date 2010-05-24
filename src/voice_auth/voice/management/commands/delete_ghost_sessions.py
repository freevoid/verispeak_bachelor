from django.core.management.base import BaseCommand
from django.conf import settings

from datetime import datetime, timedelta

from voice.models import RecordSession, VerificationProcess

class Command(BaseCommand):
    help = ('Delete relatively old (which is tuned with settings.MAX_SESSION_TTL) record sessions without uploaded utterances.')
    requires_model_validation = True

    def handle(self, **options):
        max_ttl = timedelta(minutes=settings.MAX_SESSION_TTL)
        sessions_to_delete = RecordSession.objects\
                .filter(uploadedutterance__isnull=True,
                        created_time__lte=datetime.now()-max_ttl)
                
        deleted_count = sessions_to_delete.count()
        sessions_to_delete.delete()
        VerificationProcess.objects\
                .filter(target_session__isnull=True).delete()
        print "Deleted %d sessions" % deleted_count

