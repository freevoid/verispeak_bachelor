#!/usr/bin/env python
import os
from itertools import imap, islice
import logging

import verispeak
from micromake import walk_on_files, need_rebuild, dir_is_older
from util import force_existence

def _wav_to_features(dirpath, processor):
    def try_to_process(filename):
        try:
            w = processor.process(filename)
        except verispeak.exceptions.InsufficientUtteranceLength, e:
            return None
        else:
            return w

    for subdir in os.listdir(dirpath):
        listing = verispeak.wave.listdir(os.path.join(dirpath, subdir))
        yield (subdir, imap(try_to_process, listing))

def wav_to_features(wav_dir, features_dir, processor=verispeak.processors.CommonMFCCStack()):
    for id, features in _wav_to_features(wav_dir, processor):
        logging.info("Processing wav files from '%s/%s/'..", wav_dir, id)

        outdir = os.path.join(features_dir, id)
        logging.info("Going to save to '%s'", outdir)
        force_existence(outdir)
        if not dir_is_older(outdir, os.path.join(wav_dir, id)):
            logging.info("Everything seems to be up to date, omitting.")
            continue
        for i, feature in enumerate(features):
            if feature is None:
                logging.warning("SKIPPED FILE %s", i)
                continue
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
            trained_model = verispeak.api._enroll(train_samples, model, train_parameters=train_parameters, fail_silently=True)
            if trained_model is not None:
                model.dump_to_file(outfile)
    logging.info("Everything is up to date!")

#def silence_test(cfg):
#    for w in cfg.W_RANGE:

def main(cfg):
    wav_to_features(cfg.WAV_DIR, cfg.FEATURES_DIR)
    ubm = verispeak.util.load_pickled_file(cfg.UBM_PATH)
    features_to_models(cfg.FEATURES_DIR, cfg.MODELS_DIR,
            cfg.MODEL_FACTORY, cfg.ENROLL_COUNT, train_parameters={'ubm': ubm})

    logging.info("Everything is up to date.")
    return 0

if __name__=='__main__':
    import sys
    assert len(sys.argv) == 2
    config_dotted_name = sys.argv[1]

    from config import Config
    cfg = Config.read_config(config_dotted_name)
    sys.exit(main(cfg))

