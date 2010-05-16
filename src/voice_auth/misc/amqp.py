# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import sys
from threading import Thread

from amqplib import client_0_8 as amqp
from django.conf import settings

from logic.context import Context
from logic.exceptions import CoreException
from misc import json
from misc.snippets import log_exception, raise_on_except

TIMESTAMP_FORMAT = '%d.%m.%Y-%H:%M:%S'

CoreException = BaseException
class AmqpError(CoreException): pass

def connection_settings():
    ret = {'host': settings.AMQP_HOST}
    if settings.AMQP_PASSWORD:
        ret['password'] = settings.AMQP_PASSWORD
    return ret

class AmqpClient(Thread):
    '''
        Start listening queue 'module_name' and transfer messages to self.callback
    '''
    def __init__(self, callback_func, queue=None, use_ctx=True):
        super(AmqpClient, self).__init__()
        self.callback_func = callback_func
        if queue is None:
            queue = '.'.join([callback_func.__module__.rsplit('.', 1)[-1], callback_func.__name__])
        params = connection_settings()
        with amqp.Connection(**params) as conn:
            self.chan = conn.channel()
            logging.info('Starting consume queue "%s"...' % queue)
            callback = self.callback_ctx if use_ctx else self.callback
            consumer_tag = self.chan.basic_consume(queue=queue, no_ack=False, callback=callback)
            logging.info('Listening')
            while True:
                try:
                    self.chan.wait()
                except KeyboardInterrupt:
                    logging.debug('Interrupted by user')
                    self.interrupted_by_user = True
                    break
            self.chan.basic_cancel(consumer_tag=consumer_tag)
            self.chan.close()
    
    # TODO callback is a copypasted version of callback_ctx, fix it
    def callback_ctx(self, amqp_message):
        # TODO handle possible json.loads errors
        ctx = Context.from_dict(json.loads(amqp_message.body))
        
        try:
            self.callback_func(ctx)
        except BaseException as e:
            log_exception('AmqpClient callback exception:\n')
            
        try:
            self.chan.basic_ack(amqp_message.delivery_tag)
        except BaseException as e:
            logging.error('AmqpClient could not send ACK to queue: %s' % e)
        
    def callback(self, amqp_message):
        # TODO handle possible json.loads errors
        data = json.loads(amqp_message.body)
        
        try:
            self.callback_func(data)
        except BaseException as e:
            log_exception('AmqpClient callback exception:\n')
            
        try:
            self.chan.basic_ack(amqp_message.delivery_tag)
        except BaseException as e:
            logging.error('AmqpClient could not send ACK to queue: %s' % e)

queues = ['merchant_payment.deferred_start', 'merchant_payment.deferred_stage2',
            'transfer.deferred_start', 'workflow.process_fraudtest_result',
            'product_payment.deferred_stage2',
            'eport.packet_mode',
            'replenishment.deferred_start', 'replenishment.deferred_stage2']

def setup_queues():
    logging.info('Setting up queues %s...' % queues)
    with amqp.Connection(host=settings.AMQP_HOST) as conn:
        chan = conn.channel()
        chan.exchange_declare(exchange=settings.AMQP_EXCHANGE_NAME, type="direct", durable=True, auto_delete=False)
        for queue in queues:
            chan.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
            chan.queue_bind(queue=queue, exchange=settings.AMQP_EXCHANGE_NAME, routing_key=queue)

@raise_on_except(AmqpError)
def send_message(dst, ctx):
    _send_message_raw(dst, ctx.to_dict())

def _send_message_raw(dst, data):
    amqp_message = amqp.Message(json.dumps(data))
    params = connection_settings()
    with amqp.Connection(**params) as conn:
        with conn.channel() as chan:
            chan = conn.channel()
            amqp_message.properties['delivery_mode'] = 2 # message is persistent
            chan.basic_publish(amqp_message, settings.AMQP_EXCHANGE_NAME, routing_key=dst, mandatory=True)

send_message_raw = raise_on_except(AmqpError)(_send_message_raw)

