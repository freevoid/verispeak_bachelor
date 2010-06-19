class VerispeakException(Exception):
    '''
    Base exception class for all exceptions in verispeak package.
    '''
    pass

class InsufficientUtteranceLength(VerispeakException):
    def __init__(self, length, min_length):
        self.length = length
        self.min_length = min_length
        super(InsufficientUtteranceLength, self).__init__()

    def __repr__(self):
        return "Insufficient to adequately verificate: %.2f < %.2f" (self.length, self.min_length)

class TooBigUtteranceLength(VerispeakException):
    def __init__(self, length, max_length):
        self.length = length
        self.max_length = max_length
        super(TooBigUtteranceLength, self).__init__()

    def __repr__(self):
        return "Very long utterances not supported: %.2f > %.2f" (self.length, self.max_length)

