# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import sys
from threading import Thread

from amqplib import client_0_8 as amqp
from django.conf import settings

from misc import json
from misc.snippets import log_exception, raise_on_except

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
        ctx = json.loads(
                json.loads(amqp_message.body)
                )
        
        try:
            self.callback_func(**ctx)
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

