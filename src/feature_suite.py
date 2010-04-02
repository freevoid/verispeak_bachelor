from base import Object
from wave import listdir, Wave
from features import CompositeFeatures

from itertools import ifilter, imap

class FeaturesSuite(Object):
    person_id = None
    features_class = None
    def __init__(self, phrase_prefix, person_id=0, features_class=CompositeFeatures):
        self.person_id = person_id
        self.phrase_prefix = phrase_prefix
        self.samples = set()
        self.features_class = features_class
        super(FeaturesSuite, self).__init__()

    def __len__(self):
        return len(self.samples)

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
        waves = imap(Wave, files)
        features = imap(self.features_class, waves)
        self.samples.update(features)
        
    def _has_prefix(self, path):
        import os.path
        basename = os.path.basename(path)
        prefix = basename.rsplit('_', 1)[0]
        return prefix == self.phrase_prefix

