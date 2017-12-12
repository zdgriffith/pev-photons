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
    p.add_argument('--extension', type=float, default=0,
                   help='Spatial extension to source hypothesis in degrees.')
    args = p.parse_args()

    if args.extension:
        inFile = args.prefix + 'all_sky/ext/skymap_ext_%s.npy' % args.extension
        outFile = args.prefix + 'all_sky/ext/p_value_skymap_ext_%s.npy' % args.extension
    else:
        inFile = args.prefix + 'all_sky/skymap.npy'
        outFile = args.prefix + 'all_sky/p_value_skymap.npy'

    # File which contains the pixels of the skymap which have
    # unique declination values.
    dec_pix = np.load('/data/user/zgriffith/pev_photons/all_sky/dec_values_512.npz')
    pixels  = dec_pix['pix_list']

    ts_map = np.load(inFile)
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

    np.save(outFile, pval_map)
