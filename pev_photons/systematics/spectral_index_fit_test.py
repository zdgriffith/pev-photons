#!/usr/bin/env python

########################################################################
# Perform a scan over the entire FOV, evaluating the TS at each pixel.
########################################################################

import argparse
import numpy as np
import logging

from skylab.ps_injector import PointSourceInjector
from pev_photons.utils.load_datasets import load_dataset
from pev_photons.utils.support import prefix

def gammaray_check(args):
    ps_llh = load_dataset('point_source', args)

    ntrials = 1000
    declination = -60
    dec = np.radians(declination)
    ra = np.pi
    alpha_list = [2.0, 2.7]
    n_list = np.arange(0,21,1)
    alpha_fits = np.zeros((len(alpha_list),len(n_list), ntrials))
    ns_fits = np.zeros((len(alpha_list),len(n_list), ntrials))
    for i, alpha in enumerate(alpha_list):
        inj= PointSourceInjector(alpha, E0=2*10**6,
                                 sinDec_bandwidth=np.sin(np.radians(2)))
        inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)
        for j, n_source in enumerate(n_list):
            print(n_source)
            a = ps_llh.do_trials(n_iter=ntrials, src_ra=ra, src_dec=dec,
                                 injector=inj, mean_signal=n_source,
                                 poisson=False)
            alpha_fits[i][j] = a['gamma']
            ns_fits[i][j] = a['nsources']
            np.save(prefix+'all_sky/alpha_fit_test_{}.npy'.format(declination), alpha_fits)
            np.save(prefix+'all_sky/ns_fit_test_{}.npy'.format(declination), ns_fits)

def bias_check(args):

    ntrials = 1000
    declination = -60
    dec = np.radians(declination)
    ra = np.pi
    alpha = 2.0
    energy_bias = np.arange(0.1, 2.00, 0.1)
    ns_fits = np.zeros((len(energy_bias), ntrials))
    flux_fits = np.zeros((len(energy_bias), ntrials))
    n_source = 20
    for i, ratio in enumerate(energy_bias):
        args.seed = np.random.randint(10**7)
        print(i)
        ps_llh = load_dataset('point_source', args, bias=ratio)
        inj= PointSourceInjector(alpha, E0=2*10**6,
                                 sinDec_bandwidth=np.sin(np.radians(2)))
        inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)
        a = ps_llh.do_trials(n_iter=ntrials, src_ra=ra, src_dec=dec,
                             injector=inj, mean_signal=n_source,
                             poisson=False)
        ns_fits[i] = a['nsources']
        flux_fits[i] = inj.mu2flux(a['nsources'])
        np.save(prefix+'all_sky/ns_fit_test_bias.npy', ns_fits)
        np.save(prefix+'all_sky/flux_fit_test_bias.npy', flux_fits)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test fitting of ns and alpha.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    #gammaray_check(args)
    bias_check(args)
