class Object(object):
    def __unicode__(self):
        return u"%s" % self.__dict__
    def __str__(self):
        return self.__unicode__()
    def __repr__(self):
        return u"<%s.%s: %s>" % (
                self.__class__.__module__, 
                self.__class__.__name__,
                self.__str__())

class SerializableObject(Object):
    def serialize(self):
        import cPickle
        return cPickle.dumps(self.serializable(), -1)

    def dump_to_file(self, filename_or_file):
        if isinstance(filename_or_file, basestring):
            f = open(filename_or_file, "wb")
        else:
            f = filename_or_file
        f.write(self.serialize())
        f.close()
        return True

    def serializable(self):
        return self

    @staticmethod
    def deserialize(unpickled_data):
        return unpickled_data

    @classmethod
    def load(cls, filename):
        import cPickle
        f = open(filename)
        return cls.deserialize(cPickle.load(f))

