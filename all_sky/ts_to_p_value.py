#!/usr/bin/env python

########################################################################
# Converts the TS map to a p-value map using background trials,
# rather than relying on chi2 approximations.
########################################################################

import argparse
import healpy as hp
import numpy as np
from glob import glob

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Convert TS map to p-value map.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='The base directory for file storing.')
    p.add_argument('--inFile', type=str,
                   default='all_sky/comparison/skymap_512.npy',
                   help='The output file name.')
    p.add_argument('--outFile', type=str,
                   default='all_sky/comparison/p_value_skymap.npy',
                   help='The output file name.')
    args = p.parse_args()

    # File which contains the pixels of the skymap which have
    # unique declination values.
    dec_pix = np.load('/data/user/zgriffith/pev_photons/all_sky/dec_values_512.npz')
    pixels  = dec_pix['pix_list']

    ts_map = np.load(args.prefix + args.inFile)
    n_decs = len(pixels) 
    pval_map = np.ones_like(ts_map)
    
    # For each unique declination, calculate the fraction of bg trials
    # which have a TS value above the true value.
    for dec_i in range(n_decs):
        print(dec_i)
        f_list = glob(args.prefix+'all_sky/dec_trials/dec_%s_job_*' % dec_i)
        trials = []
        for f in f_list:
            a = np.load(f)
            trials.extend(a)
        pix = pixels[dec_i]
        above_true  = np.greater_equal(trials, ts_map[pix][:, np.newaxis])
        pval_map[pix] = np.sum(above_true, axis=1)/float(len(trials))

    np.save(args.prefix + args.outFile, pval_map)
