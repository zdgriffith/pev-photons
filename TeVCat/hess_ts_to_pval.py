#!/usr/bin/env python

########################################################################
# Converts the TS map to a p-value map using background trials,
# rather than relying on chi2 approximations. For HESS sources.
########################################################################

import argparse
import numpy as np
from glob import glob

import healpy as hp

from utils.support import prefix, resource_dir

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Convert TS map to p-value map.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--inFile', type=str,
                   default='hess_sources_fit_results.npy',
                   help='The input file name.')
    p.add_argument('--outFile', type=str,
                   default='hess_sources_p_values.npy',
                   help='The output file name.')
    p.add_argument('--use_original_trials', action='store_true', default=False,
                   help='Use the original background trials rather those you generated on your own.')
    args = p.parse_args()

    dec_pix = np.load(resource_dir+'dec_values_512.npz')
    pixels = dec_pix['pix_list']
    n_decs = len(pixels) 

    sources = np.load(resource_dir+'hess_sources.npz')
    src_pix = hp.ang2pix(512,
                         np.pi/2. - np.radians(sources['dec']),
                         np.radians(sources['ra']))
    ts = np.load(prefix+'TeVCat/'+args.inFile)['TS']
    p_val = np.zeros(len(ts))
    
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
        for i, p in enumerate(src_pix):
            if p in pix:
                p_val[i] = np.sum(np.greater(trials,ts[i]))/float(len(trials))

    print(p_val)
    np.save(prefix + 'TeVCat/'+args.outFile, p_val)
