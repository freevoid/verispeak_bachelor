import logging
import os
import sys
import time

# NOTE for a full list of available queues see logic.amqp.queues
def launch(callback_func_name, queue_name=None, use_ctx=True):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    import settings # activating logging settings
 
    if not queue_name:
        queue_name = callback_func_name   
    def start():
        func_name = callback_func_name
        if func_name[-1] == '/':
            func_name = func_name[:-1]
        module_name, func_name = func_name.rsplit('.', 1)
        logging.info('Importing module "%s"...' % module_name)
    
        module = __import__(module_name, fromlist=[func_name])
        callback_func = getattr(module, func_name)

        from misc.amqp import AmqpClient, setup_queues
        while True:
            try:
                logging.info('Creating AmqpClient...')
                setup_queues()
                c = AmqpClient(callback_func, queue_name, use_ctx)
                if getattr(c, 'interrupted_by_user', False):
                    break
            except IOError:
                from misc.snippets import log_exception
                log_exception('RabbitMQ connection failed')
                logging.info('Sleep for 10 seconds before reconnect ..........')
                time.sleep(10)

    start()
    '''
    if len(sys.argv) <= 1:
        start()
    else:
        from __init__ import log_files
        from misc.daemon_runner import App
        App(start, pidfiles_path=settings.PIDFILES_PATH, files_preserve=log_files()).do_action()
    '''
