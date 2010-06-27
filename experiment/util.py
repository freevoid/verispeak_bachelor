import numpy as np
import logging
import os

def load_det_from_txt(filename):
    logging.info("Opening datafile '%s'..", filename)
    det = np.loadtxt(filename, unpack=True)
    print "OPENED", det.shape
    return det

def save_det_to_txt(filename, det):
    np.savetxt(filename, det)

def force_existence(path):
    if not os.access(path, os.F_OK):
        os.system('mkdir -p "%s"' % path)

