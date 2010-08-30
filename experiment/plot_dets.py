#!/usr/bin/env python
#-*- coding: utf-8 -*-
from micromake import walk_on_files

import os
import logging
import numpy
import glob

from matplotlib import pyplot
#from verispeak.ruplot import pyplot

from util import load_det_from_txt

DEFAULT_FORMAT = 'pdf'

OMEGA_STEP = 50

import calc_data

def plot_eer_from_k(male_eers, female_eers):
    f = _plot_eer(male_eers, style='-bD', label=u'Мужчины')
    _plot_eer(female_eers, axes=f.axes[0], style='-g^', label=u'Женщины')
    f.axes[0].legend()
    return f

def plot_eer_from_n(male_eers, female_eers):
    f = _plot_eer(male_eers, style='-bD', label=u'Мужчины')
    _plot_eer(female_eers, axes=f.axes[0], style='-g^', label=u'Женщины', xlabel=u'Количество фраз для обучения')
    f.axes[0].legend()
    return f

def _plot_eer(eers, xlabel=u'Количество компонент',
        axes=None, style='-bD', label=None):
    if axes is None:
        f = pyplot.figure()
        ax = f.add_subplot(111)
    else:
        f = axes.figure
        ax = axes

    eers = eers.T
    x = eers[0] if eers[0][1] != eers[0][0] else eers[1]
    y = eers[-1]*100 # in percents
    ax.plot(x, y, style, label=label)

    ax.grid(True)
    ax.set_ylabel(u'Частота равнозначной ошибки, %')
    ax.set_xlabel(xlabel)

    return f

def _plot_prob(det, eer=None, delta=None, axes=None,
        label_postfix='', fn_style='gD-', fp_style='r^-'):
    if axes is None:
        f = pyplot.figure()
        ax = f.add_subplot(111)
    else:
        f = axes.figure
        ax = axes

    if label_postfix:
        label_postfix = '(%s)' % label_postfix
    det = calc_data.canonize_det(det)
    if eer is None: eer = calc_data.find_eer(det)
    if delta is None: delta = calc_data._calc_delta(det)

    f = pyplot.figure()
    ax = f.add_subplot(111)

    omega, target_y, impostor_y = det.T.copy()

    target_y = 1 - target_y
    impostor_y *= 100
    target_y *= 100
    eer *= 100
    
    min_target, max_impostor, d = delta
    min_target -= OMEGA_STEP

    imax = omega.searchsorted(max_impostor) + 1
    tmin = omega.searchsorted(min_target)

    ax.plot(omega[tmin:], target_y[tmin:], fn_style, label=u'Ложный отрицательный %s' % label_postfix)
    ax.plot(omega[:imax], impostor_y[:imax], fp_style, label=u'Ложный положительный %s' % label_postfix)

    ax.vlines([min_target, max_impostor], *ax.get_ylim(), linestyles='dotted', color='lightgreen', label='_nolegend_')
    ax.hlines([eer], *ax.get_xlim(), linestyles='dashed', label=u'Граница частоты равнозначной ошибки')
    
    ax.legend()

    '''
    yticks = ax.get_yticks()
    xticks = ax.get_xticks()
    ax.set_yticks(numpy.concatenate((yticks, [eer])))
    ax.set_xticks(numpy.concatenate((xticks, delta[:2])))
    #numpy.arange(omega[0], omega[-1], OMEGA_STEP).tolist())
    '''

    ax.grid(True)

    ax.set_ylabel(u'Вероятность ошибки, %')
    ax.set_xlabel(u'Порог вхождения')

    return f

def plot_overall(det_list, outdir, format=DEFAULT_FORMAT):
    outfile = os.path.join(outdir, '.'.join(['overall', format]))

    logging.info("Plotting aggregated info..")
    pyplot.figure()
    n = len(det_list)
    omega0 = det_list[0][0]
    target_y_sum = numpy.zeros(omega0.shape)
    impostor_y_sum = target_y_sum.copy()

    for det in det_list:
        omega, target_y, impostor_y = det
        target_y = 1 - target_y
        target_y *= 100
        impostor_y *= 100
        target_y_sum += target_y
        impostor_y_sum += impostor_y
        #pyplot.plot(omega, target_y, color='lightgreen')
        #pyplot.plot(omega, impostor_y, color='#ffaaaa')
    logging.info("Saving aggregated info in '%s'", outfile)

    pyplot.plot(omega0, target_y_sum / n, color='green')
    pyplot.plot(omega0, impostor_y_sum / n, color='red')

    pyplot.ylabel(u'Вероятность ошибки, %')
    pyplot.xlabel(u'Порог вхождения')
    pyplot.savefig(outfile)

def plot_det(det, outfile):
    return
    #ext = os.path.splitext(outfile)[1]
    omega, target_y, impostor_y = det

    pyplot.figure()
    target_y = 1 - target_y
    #pyplot.plot(target_y, impostor_y)
    pyplot.plot(omega, target_y, color='green')
    pyplot.plot(omega, impostor_y, color='red')
    pyplot.savefig(outfile)
    #return det

def plot_dets_from_txt(iddets, out_dir, format=DEFAULT_FORMAT):
    for id, det in iddets:
        outfile = os.path.join(out_dir, '.'.join([id, format]))
        plot_det(det, outfile)

def plot_dets_configured(cfg):
    plot_dets_from_txt(load_dets(cfg.DETS_DIR), cfg.PLOT_DIR,
            format=cfg.PLOT_FORMAT)

def walk_on_dets(dets_dir):
    for filename in glob.iglob(os.path.join(dets_dir, '???.txt')):
        id = os.path.basename(os.path.splitext(filename)[0])
        yield id, filename

def load_dets(dets_dir):
    return ((id, load_det_from_txt(filename)) for (id, filename) in walk_on_dets(dets_dir))


def plot_overall_configured(cfg):
    dets = zip(*load_dets(cfg.DETS_DIR))[1]
    plot_overall(dets, cfg.PLOT_DIR, format=cfg.PLOT_FORMAT)

main = plot_overall_configured

if __name__=='__main__':
    import sys
    assert len(sys.argv) == 2
    config_dotted_name = sys.argv[1]
    from config import Config
    cfg = Config.read_config(config_dotted_name)
    main(cfg)

    #logging.info("DETS successfully calculated and saved.")

