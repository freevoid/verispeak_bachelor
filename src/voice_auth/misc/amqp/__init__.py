import logging
import sys
from threading import Thread
from functools import partial

from amqplib import client_0_8 as amqp
from django.conf import settings

from misc import json
from misc.snippets import log_exception, raise_on_except, autodiscover

from client import AmqpClient, AmqpError, connection_settings

class QueueTracker:
    _registry = []

    @classmethod
    def register(cls, queue_name):
        cls._registry.append(queue_name)
register_queue = QueueTracker.register

def setup_queues():
    logging.info('Setting up queues %s...' % QueueTracker._registry)
    with amqp.Connection(host=settings.AMQP_HOST) as conn:
        chan = conn.channel()
        chan.exchange_declare(exchange=settings.AMQP_EXCHANGE_NAME, type="direct", durable=True, auto_delete=False)
        for queue in QueueTracker._registry:
            chan.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
            chan.queue_bind(queue=queue, exchange=settings.AMQP_EXCHANGE_NAME, routing_key=queue)

@raise_on_except(AmqpError)
def send_message(dst, **ctx):
    _send_message_raw(dst, json.dumps(ctx))

def _send_message_raw(dst, data):
    amqp_message = amqp.Message(json.dumps(data))
    params = connection_settings()
    with amqp.Connection(**params) as conn:
        with conn.channel() as chan:
            chan = conn.channel()
            amqp_message.properties['delivery_mode'] = 2 # message is persistent
            chan.basic_publish(amqp_message, settings.AMQP_EXCHANGE_NAME, routing_key=dst, mandatory=True)
send_message_raw = raise_on_except(AmqpError)(_send_message_raw)

autodiscover = partial(autodiscover, cb_module_name='queues', site_cls=QueueTracker)
