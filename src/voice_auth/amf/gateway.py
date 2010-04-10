from pyamf.remoting.gateway.django import DjangoGateway

OK = "OK\n"
import logging

def upload_sound(request, data):
    logging.error("GOT SOUND! %s" % type(data))
    return OK

services = {
    'sound.upload': upload_sound
    # could include other functions as well
}

upload_gateway = DjangoGateway(services)

