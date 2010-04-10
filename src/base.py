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

class ScoreObject(Object):
    def __flatten__(self):
        return [list(self)]

    def _force_length(self, length):
        assert len(self) > length
        class Dummy:
            def __len__(self):
                return length
            def __flatten__(self):
                return [range(length)]
            flatten_features = None
        d = Dummy()
        
        [(unified, x)] = self.unify_size(d)
        return unified

    def unify_size(self, other):
        import misc
        import itertools
        flat_self = self.flatten_features if self.flatten_features is not None else self.__flatten__()
        flat_other = other.flatten_features if other.flatten_features is not None else other.__flatten__()

        zipper = itertools.izip(flat_self, flat_other)
        for self_list, other_list in zipper:
            self_list, other_list = misc.coerce_no_sf(self_list, other_list)
            n1, n2 = len(self_list), len(other_list)
            overlap = n1 - n2
            if overlap > 0:
                self_list = self_list[:-overlap]
            elif overlap < 0:
                other_list = other_list[:overlap]
            yield self_list, other_list

