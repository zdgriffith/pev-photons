#!/usr/bin/env python

########################################################################
# Converts the TS map to a p-value map using background trials,
# rather than relying on chi2 approximations.
########################################################################

import argparse
import healpy as hp
import numpy as np

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Convert TS map to p-value map.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='The base directory for file storing.')
    p.add_argument('--inFile', type=str,
                   default='all_sky/skymap.npy',
                   help='The output file name.')
    p.add_argument('--outFile', type=str,
                   default='all_sky/p_value_skymap.npy',
                   help='The output file name.')
    args = p.parse_args()

    # File which contains uniqe the pixels of the skymap which have
    # unique declination values.
    dec_pix = np.load('/data/user/zgriffith/all_sky/dec_vals.npz')
    pixels  = dec_pix['pix_list']

    ts_map = np.load(args.prefix + args.inFile)
    ts_map = hp.ud_grade(ts_map, nside_out=512)
    n_jobs = len(pixels) 
    pval_map = np.ones_like(ts_map)
    
    # For each unique declination, calculate the fraction of bg trials
    # which have a TS value above the true value.
    n_trials = 500000
    for job in range(n_jobs):
        a = np.load(args.prefix+'all_sky/dec_jobs/dec_TS_job_%s.npz' % float(job))
        trials = a['indv_trials'][0:n_trials]
        pix = pixels[job]
        for p in pix:
            above_true  = np.greater_equal(trials, ts_map[p])
            pval_map[p] = np.sum(above_true)/float(len(trials))

    np.save(args.prefix + args.outFile, pval_map)
