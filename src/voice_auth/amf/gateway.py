from pyamf.remoting.gateway.django import DjangoGateway

OK = "OK\n"
import logging

def upload_sound(request, data):
    logging.error("GOT SOUND! %s %s" % (type(data), dir(data)))
    return OK

def init_upload(request, data):
    info = data
    logging.error("GOT INIT REQUEST: %s" % info)
    info = "from %s '%s'" % (request.META.REMOTE_ADDR, data)
    return OK

services = {
    'sound.upload': upload_sound,
    'sound.init': init_upload
    # could include other functions as well
}

upload_gateway = DjangoGateway(services)

