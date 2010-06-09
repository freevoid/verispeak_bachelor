from verispeak.scoring import DTWScore
from verispeak.misc import calc_treshhold
from verispeak.base import Object
from verispeak.wave import listdir

from itertools import ifilter

class FeaturesSuite(Object):
    person_id = None
    def __init__(self, phrase_prefix, person_id=0):
        self.person_id = person_id
        self.phrase_prefix = phrase_prefix
        self.samples = set()
        super(FeaturesSuite, self).__init__()

    def add_sample(self, features):
        self.samples.add(features)

    def del_sample(self, features):
        try:
            self.samples.remove(features)
        except KeyError:
            pass

    def read_dir(self, path):
        files = ifilter(self._has_prefix,
                listdir(path))

    def _has_prefix(self, path):
        import os.path
        basename = os.path.basename(path)
        prefix = basename.rsplit('_', 1)[0]
        return prefix == self.phrase_prefix

    def calc_treshhold(self, score_class=DTWScore, other=[]):
        calc_treshhold(score_class, self.samples, other)

