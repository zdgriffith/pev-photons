#!/usr/bin/env python

########################################################################
# Calculates the sensitivity to each HESS source's
# declination and spectral index 
########################################################################

import argparse
import numpy as np

from skylab.ps_injector import PointSourceInjector

from pev_photons.utils.load_datasets import load_dataset
from pev_photons.utils.support import prefix, resource_dir

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
    ps_llh = load_dataset('point_source', args)

    hess = np.load(resource_dir+'hess_sources.npz')
    sens = list()
    disc = list()

    for i, alpha in enumerate(hess['alpha']):
        if np.isnan(alpha):
            sens.append(np.nan)
            disc.append(np.nan)
        else:
            dec = np.radians(hess['dec'][i])
            inj= PointSourceInjector(alpha, E0=1e6,
                                     sinDec_bandwidth=np.sin(np.radians(2)))
            inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)
            result = ps_llh.weighted_sensitivity([0.5, 2.87e-7], [0.9, 0.5],
                                                 inj=inj,
                                                 eps=1.e-2,
                                                 n_bckg=10000,
                                                 n_iter=1000,
                                                 src_ra=np.pi, src_dec=dec)
            sens.append(result[0]["flux"][0])
            disc.append(result[0]["flux"][1])
            print(sens)

    a = dict()
    a['name'] = hess['name']
    a['sensitivity'] = sens
    a['discovery_potential'] = disc

    np.savez(prefix+'TeVCat/hess_sens.npz', **a)