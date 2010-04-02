from base import Object
from scoring import DTWScore
from misc import calc_treshhold

class Decision(Object):
    treshhold = 0
    scoring_class = None
    samples_suite = None

    def __init__(self, samples_suite, scoring_class=DTWScore):
        super(Decision, self).__init__()
        self.samples_suite = samples_suite
        self.scoring_class = scoring_class

        self.treshhold = self.calc_treshhold()

    def recalc_treshhold(self, other_features=[], other_suites=[]):
        recalculated = self.calc_treshhold()
        self.treshhold = recalculated
        return recalculated
 
    def calc_treshhold(self, other_features=[], other_suites=[]):
        if other_suites != []:
            other_features = sum((list(x.samples) for x in other_suites), [])

        return calc_treshhold(self.scoring_class, list(self.samples_suite.samples), other_features)       

    def decise(self, target_wave):
        target_features = self.samples_suite.features_class(target_wave)
        scoring = self.scoring_class(target_features)
        average_score = scoring.suite_average_score(self.samples_suite)

        return average_score < self.treshhold



