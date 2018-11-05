#!/usr/bin/env python

########################################################################
# Calculates the sensitivity to each HESS source's
# declination and spectral index
########################################################################

import argparse
import numpy as np

from skylab.ps_injector import PointSourceInjector

from pev_photons import utils

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='HESS source sensitivity calculation',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    # Load the dataset.
    ps_llh = utils.load_dataset('point_source', ncpu=args.ncpu, seed=args.seed)

    hess = np.load(utils.prefix+'resources/hess_sources.npz')
    sens = list()

    for i, alpha in enumerate(hess['alpha']):
        if np.isnan(alpha):
            sens.append(np.nan)
        else:
            dec = np.radians(hess['dec'][i])
            inj= PointSourceInjector(alpha, E0=2e6,
                                     sinDec_bandwidth=np.sin(np.radians(2)))
            inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)
            result = ps_llh.weighted_sensitivity([0.5], [0.9],
                                                 inj=inj,
                                                 eps=1.e-2,
                                                 n_bckg=10000,
                                                 n_iter=1000,
                                                 src_ra=np.pi, src_dec=dec)
            sens.append(result[0]["flux"][0])
            print(sens)

    a = dict()
    a['name'] = hess['name']
    a['sensitivity'] = sens

    np.savez(utils.prefix+'TeVCat/hess_sens.npz', **a)
