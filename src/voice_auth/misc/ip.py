import socket, struct

fmt = 'L' if len(struct.pack('L', 0)) == 4 else 'i'
try:
    struct.unpack(fmt, '0000')
except struct.error:
    raise NotImplementedError("Architecture not supported")

def dotted_quad_to_num(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack(fmt,socket.inet_aton(ip))[0]

def num_to_dotted_quad(n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack(fmt,n))

def ip_wrapper_property(ip_attr_name):

    def getter(self):
        return num_to_dotted_quad(getattr(self, ip_attr_name))

    def setter(self, dotted_quad):
        setattr(self, ip_attr_name,
                dotted_quad_to_num(dotted_quad))

    return property(getter, setter)


