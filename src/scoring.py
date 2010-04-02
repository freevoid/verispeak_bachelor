from base import Object
from dtw import dtw
import math

class Score(Object):
    def __init__(self, original):
        super(Score, self).__init__()
        self.original = original

    def score(self, other):
        return 0.0

    def suite_average_score(self, suite):
        from itertools import imap
        scores_sum = sum(imap(self.score, suite.samples))
        return float(scores_sum)/len(suite)

class DTWScore(Score):
    def __init__(self, original, constraint_ratio=0.1, p=1):
        super(DTWScore, self).__init__(original)
        self.constraint_ratio = constraint_ratio
        self.p = p
        if len(original) > 300:
            class Dummy:
                def __flatten__(self):
                    return [range(500)]
                flatten_features = None
            d = Dummy()
            [(unified_flatten_features, x)] = original.unify_size(d)
            original.flatten_features = [unified_flatten_features]

    def score(self, other):
        score = 0.0
        i=0
        for a1, a2 in self.original.unify_size(other):
            i+=1
            n = len(a1)
            assert(n == len(a2))
            d = dtw(n, int(self.constraint_ratio*n))
            score += d.fastdynamic(a1, a2)**2
        return score**(1/2.0)#math.sqrt(score)

