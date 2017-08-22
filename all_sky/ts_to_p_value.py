#!/usr/bin/env python

##########################################
## Converts the TS map to a p-value map ##
## using background trials, rather than ##
## relying on chi2 approximations       ##
##########################################

import argparse
import healpy as hp
import numpy as np

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Create an all sky TS map',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--inFile', dest='inFile', type = str,
                   default = 'all_sky/skymap.npy',
                   help    = 'input file name')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'all_sky/p_value_skymap.npy',
                   help    = 'input file name')
    args = p.parse_args()

    ts_map   = np.load(args.prefix+args.inFile) # test statistic map
    pval_map = np.ones_like(ts_map)
    decPix   = np.load('/data/user/zgriffith/all_sky/dec_vals.npz') # unique declination pixels the skymap
    pixels   = decPix['pix_list']
    njobs    = len(pixels) 
    
    #For each unique declination, calculate the fraction of bg trials
    #which have a TS value above the true value
    for job in range(njobs):
        print(job)
        a      = np.load('/data/user/zgriffith/skylab/dec_TS_job_%s.npz' % float(job))
        trials = a['indv_trials'][0:500000]
        pix    = pixels[job]
        for p in pix:
            pval_map[p] = np.sum(np.greater_equal(trials,ts_map[p]))/float(len(trials))

    np.save(args.prefix+args.outFile, pval_map)
