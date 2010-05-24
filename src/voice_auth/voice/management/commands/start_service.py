from django.core.management.base import BaseCommand
from django.conf import settings

from misc.amqp import service_launch

class Command(BaseCommand):
    help = ('Starts amqp consumer')
    requires_model_validation = True

    def handle(self, service_name, **options):
        print service_name
        service_launch.launch(service_name)

