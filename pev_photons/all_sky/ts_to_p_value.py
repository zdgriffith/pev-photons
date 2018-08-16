#!/usr/bin/env python

########################################################################
# Converts the TS map to a p-value map using background trials,
# rather than relying on chi2 approximations.
########################################################################

import os
import argparse
import numpy as np
from glob import glob

import healpy as hp

from pev_photons.utils.support import prefix, resource_dir

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Convert TS map to p-value map.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--use_original_trials', action='store_true', default=False,
                   help=('Use the original background trials'
                         'rather those you generated on your own.'))
    args = p.parse_args()

    inFile = os.path.join(prefix, 'all_sky/skymap.npy')
    outFile = os.path.join(prefix, 'all_sky/p_value_skymap.npy')

    # File which contains the pixels of the skymap which have
    # unique declination values.
    dec_pix = np.load(resource_dir+'dec_values_512.npz')
    pixels = dec_pix['pix_list']

    ts_map = np.load(inFile)
    n_decs = len(pixels) 
    pval_map = np.ones_like(ts_map)

    # For each unique declination, calculate the fraction of bg trials
    # which have a TS value above the true value.
    for dec_i in range(n_decs):
        print('{}/{}'.format(dec_i, n_decs))
        if args.use_original_trials:
            f_list = glob('/data/user/zgriffith/pev_photons/all_sky/dec_trials/dec_%s_job_*' % dec_i)
        else:
            f_list = glob(prefix+'all_sky/dec_trials/dec_%s_job_*' % dec_i)
        trials = []
        for f in f_list:
            a = np.load(f)
            trials.extend(a)
        pix = pixels[dec_i]
        above_true = np.greater_equal(trials, ts_map[pix][:, np.newaxis])
        pval_map[pix] = np.sum(above_true, axis=1)/float(len(trials))

    np.save(outFile, pval_map)
