#!/usr/bin/env python
from micromake import walk_on_files

import os
import logging
import numpy
import glob

from verispeak.ruplot import pyplot

DEFAULT_FORMAT = 'pdf'

def plot_overall(det_list, outdir, format=DEFAULT_FORMAT):
    outfile = os.path.join(outdir, '.'.join(['overall', format]))

    logging.info("Plotting aggregated info..")
    pyplot.figure()
    for det in det_list:
        omega, target_y, impostor_y = det
        target_y = 1 - target_y
        pyplot.plot(omega, target_y, color='green')
        pyplot.plot(omega, impostor_y, color='red')
    logging.info("Saving aggregated info in '%s'", outfile)
    pyplot.savefig(outfile)

def plot_det(det, outfile):
    #ext = os.path.splitext(outfile)[1]
    omega, target_y, impostor_y = det

    pyplot.figure()
    target_y = 1 - target_y
    #pyplot.plot(target_y, impostor_y)
    pyplot.plot(omega, target_y, color='green')
    pyplot.plot(omega, impostor_y, color='red')
    pyplot.savefig(outfile)
    #return det

def plot_dets_from_txt(idfiles, out_dir, format=DEFAULT_FORMAT):
    for id, filename in idfiles:
        logging.info("Opening datafile '%s'..", filename)
        det = numpy.loadtxt(filename, unpack=True)
        outfile = os.path.join(out_dir, '.'.join([id, format]))
        plot_det(det, outfile)
        yield det

def plot_dets_configured(cfg):
    def walk_on_dets():
        for filename in glob.iglob(os.path.join(cfg.DETS_DIR, '*.txt')):
            id = os.path.basename(os.path.splitext(filename)[0])
            filename = os.path.join(cfg.DETS_DIR, id + '.txt')
            yield id, filename
    dets = list(plot_dets_from_txt(walk_on_dets(), cfg.PLOT_DIR,
            format=cfg.PLOT_FORMAT))

    plot_overall(dets, cfg.PLOT_DIR, format=cfg.PLOT_FORMAT)

main = plot_dets_configured

if __name__=='__main__':
    import sys
    assert len(sys.argv) == 2
    config_dotted_name = sys.argv[1]
    from config import Config
    cfg = Config.read_config(config_dotted_name)
    
    plot_dets_configured(cfg)

    #logging.info("DETS successfully calculated and saved.")

