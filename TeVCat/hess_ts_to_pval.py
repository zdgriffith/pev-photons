#!/usr/bin/env python

########################################################################
# Converts the TS map to a p-value map using background trials,
# rather than relying on chi2 approximations. For HESS sources.
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
                   default='all_sky/dec_values_512.npz',
                   help='The output file name.')
    p.add_argument('--outFile', type=str,
                   default='TeVCat/p_value_hess_sources.npy',
                   help='The output file name.')
    args = p.parse_args()

    dec_pix = np.load(args.prefix+args.inFile)
    pixels = dec_pix['pix_list']
    n_decs = len(pixels) 

    sources = np.load(args.prefix+'TeVCat/hess_sources.npz')
    src_pix = hp.ang2pix(512,
                         np.pi/2. - np.radians(sources['dec']),
                         np.radians(sources['ra']))
    ts = np.load(args.prefix+'TeVCat/true_source_pvalues.npy')
    p_val = np.zeros(len(ts))
    
    for dec_i in range(n_decs):
        print(dec_i)
        f_list = glob(args.prefix+'all_sky/dec_trials/dec_%s_job_*' % dec_i)
        trials = []
        for f in f_list:
            a = np.load(f)
            trials.extend(a)

        pix = pixels[dec_i]
        for i, p in enumerate(src_pix):
            if p in pix:
                p_val[i] = np.sum(np.greater(trials,ts[i]))/float(len(trials))

    print(p_val)
    np.save(args.prefix + args.outFile, p_val)
