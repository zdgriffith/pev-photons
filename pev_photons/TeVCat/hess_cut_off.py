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
    p.add_argument("--source", type=int, default=1,
                   help='index of source')
    p.add_argument("--Ecut", type=int, default=1,
                   help='Energy cut off in TeV.')
    args = p.parse_args()

    # Load the dataset.
    ps_llh = load_dataset('point_source', ncpu=args.ncpu, seed=args.seed)

    hess = np.load(prefix+'resources/hgps_sources.npz')
    sens = list()

    dec = np.radians(hess['dec'][args.source])
    inj= PointSourceInjector(hess['alpha'][args.source], E0=1e6,
                             Ecut=args.Ecut*1e3,
                             sinDec_bandwidth=np.sin(np.radians(2)))
    inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)
    result = ps_llh.weighted_sensitivity([0.5], [0.9],
                                         inj=inj,
                                         eps=1.e-2,
                                         n_bckg=10000,
                                         n_iter=1000,
                                         src_ra=np.pi, src_dec=dec)
    sens = result[0]["flux"][0]
    np.save(prefix+'TeVCat/cut_off/{}_Ecut_{}.npy'.format(args.source, args.Ecut), sens)
