import numpy as np

from base import Object
from wave import listdir
from processors import CommonMFCCStack

from itertools import ifilter, imap

class FeaturesSuite(Object):
    person_id = None
    speech_processor = None
    def __init__(self, phrase_prefix, person_id=0, speech_processor=CommonMFCCStack()):
        self.person_id = person_id
        self.phrase_prefix = phrase_prefix
        self._samples = set()
        self.speech_processor = speech_processor
        super(FeaturesSuite, self).__init__()

    def __len__(self):
        return len(self._samples)

    def add_samplefile(self, filename):
        self.add_sample(self.speech_processor.process(filename))

    def add_sample(self, features):
        self._samples.add(features)

    def add_samples(self, features_list):
        self._samples.update(features_list)

    def del_sample(self, features):
        try:
            self._samples.remove(features)
        except KeyError:
            pass

    @property
    def flat(self):
        for s in self.samples:
            for f in s.features:
                yield f

    def flatten(self):
        return np.fromiter(self.flat)

    @property
    def samples(self):
        return list(self._samples)

    def read_dir(self, path):
        files = ifilter(self._has_prefix,
                listdir(path))
        features = imap(self.speech_processor.process, files)
        self.add_samples(features)
        
    def _has_prefix(self, path):
        import os.path
        basename = os.path.basename(path)
        prefix = basename.rsplit('_', 1)[0]
        return prefix == self.phrase_prefix

