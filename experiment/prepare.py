#!/usr/bin/env python
import os
from itertools import imap, islice
import logging

logging.basicConfig(level=logging.DEBUG)

import verispeak
from micromake import walk_on_files, need_rebuild, dir_is_older

BASE_DIR = os.path.dirname(__file__)
WAV_DIR = os.path.join(BASE_DIR, 'wav')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
FEATURES_DIR = os.path.join(BASE_DIR, 'features')

SEARCH_PRIORITY = ()

def _wav_to_features(dirpath, processor):
    for subdir in os.listdir(dirpath):
        listing = verispeak.wave.listdir(os.path.join(dirpath, subdir))
        yield (subdir, imap(processor.process, listing))

def force_existence(path):
    if not os.access(path, os.F_OK):
        os.system('mkdir -p "%s"' % path)

def wav_to_features(wav_dir, features_dir, processor=verispeak.processors.CommonMFCCStack()):
    for id, features in _wav_to_features(wav_dir, processor):
        logging.info("Processing wav files from '%s/%s/'..", wav_dir, id)

        outdir = os.path.join(features_dir, id)
        logging.info("Going to save to '%s'", outdir)
        force_existence(outdir)
        if not dir_is_older(outdir, os.path.join(wav_dir, id)):
            logging.info("Everything seems to be up to date, omitting.")
            continue
        for (i, feature) in enumerate(features):
            outfile = os.path.join(outdir, '%02d.mfcc' % i)
            logging.info("Saving features to file '%s'..", outfile)
            feature.dump_to_file(outfile)

def features_to_models(features_dir, models_dir, model_factory,
        enroll_count=10, train_parameters={}):
    for id in os.listdir(features_dir):
        subdir_full = os.path.join(features_dir, id)
        subdir_listing = walk_on_files(subdir_full)

        enroll_samples = islice(subdir_listing, enroll_count)
        outfile = os.path.join(models_dir, '%s.gmm' % id)
        # if outfile is older than any of enroll_samples -> recreate model
        if need_rebuild(outfile, enroll_samples):
            logging.info("Rebuilding %s..", outfile)
            model = model_factory()
            train_samples = verispeak.features.concatenate_vectors(
                    imap(verispeak.util.load_pickled_file, enroll_samples))
            verispeak.api._enroll(train_samples, model, train_parameters=train_parameters)
            model.dump_to_file(outfile)
    logging.info("Everything is up to date!")


if __name__=='__main__':
    m16 = lambda: verispeak.gmm.CournapeauGMM(K=16)
    m32 = lambda: verispeak.gmm.CournapeauGMM(K=32)
    
    wav_to_features(WAV_DIR, FEATURES_DIR)
    features_to_models(FEATURES_DIR, MODELS_DIR, m16)

    logging.info("Everything is up to date.")

