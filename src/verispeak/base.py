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

class TimeSequence(Object):
    def __flatten__(self):
        if self.flatten_features is not None:
            return self.flatten_features
        else:
            self.flatten_features = list(iter(self))
            return self.flatten_features

    def _force_length(self, length):
        assert len(self) > length
        class Dummy:
            def __len__(self):
                return length
            def __flatten__(self):
                return [range(length)]
            flatten_features = None
        d = Dummy()
        
        (unified, x) = self.unify_size(d)
        return unified

    def unify_size(self, other):
        import misc
        import itertools
        flat_self = self.__flatten__()
        flat_other = other.__flatten__()

        self_list, other_list = misc.coerce_no_sf(flat_self, flat_other)
        n1, n2 = len(self_list), len(other_list)
        overlap = n1 - n2
        if overlap > 0:
            self_list = self_list[:-overlap]
        elif overlap < 0:
            other_list = other_list[:overlap]
        return self_list, other_list

