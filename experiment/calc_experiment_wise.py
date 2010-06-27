import calc_data

import collections
import numpy

def calc_delta(config_iterator):
    return aggregate_dets(config_iterator, calc_data.calc_delta)

def calc_eer(config_iterator):
    return aggregate_dets(config_iterator, calc_data.calc_eer)

def aggregate_dets(config_iterator, func):
    def yielder():
        for cfg in config_iterator:
            x = cfg.vector()
            res = func(cfg.DETS_DIR)
            if isinstance(res, collections.Iterable):
                yield x + res
            else:
                yield x + (res,)

    return numpy.array(list(yielder()))


