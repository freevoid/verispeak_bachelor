from verispeak.base import Object

class Codebook(Object):
    training_procedure = None

    def __init__(self):
        self.iterations = 0

    def likelihood(self, samples):
        return 0.0

    def train(self, train_samples, **kwargs):
        """
        Train the codebook on a train samples.

        @retval: number of iterations
        @val train_samples: iterable of numpy arrays (feature vectors)
        """
        iterations = self.training_procedure(self, train_samples, **kwargs)
        if kwargs.get('no_init'):
            self.iterations += iterations
        else:
            self.iterations = iterations
        return iterations

    def serialize(self):
        import cPickle
        return cPickle.dumps(self.serializable(), -1)
        training_procedure = self.training_procedure
        self.training_procedure = None
        dump = cPickle.dumps(self, -1)
        self.training_procedure = training_procedure
        return dump

    def dump_to_file(self, filename):
        f = open(filename, "wb")
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

