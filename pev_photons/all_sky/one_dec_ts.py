#!/usr/bin/env python

########################################################################
# Calculates the TS for a given declination
########################################################################

import argparse
import numpy as np

from pev_photons.utils.support import prefix
from pev_photons.utils.load_datasets import load_dataset

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test hotspot',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n_trials", type=int, default=100,
                   help='Number of trials')
    p.add_argument("--dec_i", type=int, default=0,
                   help='index corresponding to a declination in array')
    p.add_argument("--job", type=int, default=0,
                   help='job number')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    #Initialization of multi-year LLH object
    ps_llh = load_dataset('point_source', ncpu=args.ncpu, seed=args.seed)

    decs = np.load(prefix+'all_sky/dec_values_512.npz')['decs']

    trials = psllh.do_trials(args.n_trials, src_ra=np.pi,
                             src_dec=decs[args.dec_i])
    np.save(prefix+'all_sky/dec_trials/dec_%s_job_%s.npy' % (args.dec_i, args.job),
            trials['TS'])
