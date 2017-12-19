#!/usr/bin/env python

########################################################################
# Functions to test the behavior of the fitted spectral index.
########################################################################

import argparse
import numpy as np

from load_datasets import load_ps_dataset
from skylab.ps_injector import PointSourceInjector

def index_vs_events(ps_llh, args):
    """Test the fitted spectral index for a range of injected events
    and injected spectral indices.
    """
    
    # Initialize the range of parameters.
    fit = dict()
    fit['index_list'] = [1.5,2.0,3.0]
    fit['n_list'] = np.arange(0,21,1)

    fit['fit_index'] = np.zeros((len(fit['index_list']), len(fit['n_list']),
                                 args.ntrials))
    for i, index in enumerate(fit['index_list']):
        #Initialize injector with the given spectral index.
        inj= PointSourceInjector(index, E0=2*10**6,
                                 sinDec_bandwidth=np.sin(np.radians(2)))
        inj.fill(np.radians(args.dec), ps_llh.exp, ps_llh.mc, ps_llh.livetime)

        #For each number of injected events, get the fitted spectral index.
        for j, n_inj in enumerate(fit['n_list']):
            print(n_inj)
            a = ps_llh.do_trials(n_iter=args.ntrials,
                                 src_ra=np.radians(args.ra),
                                 src_dec=np.radians(args.dec),
                                 injector=inj, mean_signal=n_inj,
                                 poisson=False)
            fit['fit_index'][i][j] = a['gamma']
            np.save(args.prefix+'all_sky/systematics/index_vs_events.npy',
                    fit)

def fit_vs_inj_index(args):
    """Test the fitted spectral index for a fine range of injected
    spectral indices with the same injected events.
    """

    # Initialize the range of parameters.
    alpha_list = np.arange(1,3.6,0.1)

    alpha_fits = np.zeros((len(alpha_list), args.ntrials))
    for i, alpha in enumerate(alpha_list):
        print(alpha)
        #Initialize injector with the given spectral index.
        inj= PointSourceInjector(alpha, E0=2*10**6,
                                 sinDec_bandwidth=np.sin(np.radians(2)))
        inj.fill(np.radians(args.dec), ps_llh.exp, ps_llh.mc, ps_llh.livetime)
        a = ps_llh.do_trials(n_iter=args.ntrials,
                             src_ra=np.radians(args.ra),
                             src_dec=np.radians(args.dec),
                             injector=inj, mean_signal=20,
                             poisson=False)
        alpha_fits[i] = a['gamma']
        np.save(args.prefix+'all_sky/systematics/fit_vs_inj_index.npy',
                alpha_fits)

def index_vs_dec(args):
    """Test the fitted spectral index for a range of declinations
    with a set injected spectral index and events.
    """
    # Initialize the range of parameters.
    dec_list = np.arange(-60, -86, 1)

    alpha_fits = np.zeros((len(dec_list), ntrials))
    for i, dec in enumerate(np.radians(dec_list)):
        print(i)
        inj= PointSourceInjector(gamma=2.0, E0=2*10**6,
                                 sinDec_bandwidth=np.sin(np.radians(2)))
        inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)
        a = ps_llh.do_trials(n_iter=args.ntrials,
                             src_ra=np.radians(args.ra),
                             src_dec=np.radians(dec),
                             injector=inj, mean_signal=20,
                             poisson=False)
        alpha_fits[i] = a['gamma']
        np.save(args.prefix+'all_sky/systematics/index_vs_dec.npy', alpha_fits)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Functions to test the fitted spectral index.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='The base directory for file storing.')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    p.add_argument('--dec', type=float, default=-65.0,
                   help='The declination to test in degrees.')
    p.add_argument('--ra', type=float, default=180.0,
                   help='The right ascension to test in degrees.')
    p.add_argument("--ntrials", type=int, default=1000,
                   help='The number of trials to run at each point.')
    args = p.parse_args()

    ps_llh = load_ps_dataset(args)
    index_vs_events(ps_llh, args)
