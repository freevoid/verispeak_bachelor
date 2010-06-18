#!/usr/bin/env python
from micromake import walk_on_files

import os
import logging
import numpy

def plot_det(det, outfile):
    ext = os.path.splitext(outfile)[1]

def plot_dets_from_txt(idfiles, out_dir):
    for id, filename in idfiles:
        det = numpy.fromtxt(filename)
        n = det.size
        det = det.reshape((3, n//3))
        outfile = os.path.join(out_dir, id + '.pdf')
        plot_det(det, outfile)

def plot_dets_configured(cfg):
    def walk_on_dets():
        for id_txt in os.listdir(cfg.DETS_DIR):
            id = os.path.splitext(id_txt)[0]
            filename = os.path.join(cfg.DETS_DIR, id_txt)
            yield id, filename
    return plot_dets_from_txt(walk_on_dets(), cfg.PLOT_DIR)

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)

    import sys
    assert len(sys.argv) == 2
    config_dotted_name = sys.argv[1]
    from config import Config
    cfg = Config.read_config(config_dotted_name)

    #logging.info("DETS successfully calculated and saved.")

