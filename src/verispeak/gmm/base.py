from verispeak.base import SerializableObject

class Codebook(SerializableObject):
    training_procedure = None

    def __init__(self):
        self.iterations = 0

    def likelihood(self, samples):
        return 0.0

    def train(self, train_samples, *args, **kwargs):
        """
        Train the codebook on a train samples.

        @return: number of iterations
        @param train_samples: iterable of numpy arrays (feature vectors)
        """
        iterations = self.training_procedure(self, train_samples, *args, **kwargs)
        if kwargs.get('no_init'):
            self.iterations += iterations
        else:
            self.iterations = iterations
        return iterations

class GMMBase(Codebook):
    def get_params(self):
        return NotImplemented

    def set_params(self, w, mu, va):
        raise NotImplementedError

