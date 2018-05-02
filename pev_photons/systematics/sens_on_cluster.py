#!/usr/bin/env python

########################################################################
# Calculate sensitivity as a function of declination.
########################################################################

import argparse
import numpy as np

from skylab.ps_injector import PointSourceInjector
from pev_photons.utils.load_datasets import load_systematic_dataset
from pev_photons.utils.support import prefix

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Calculate sensitivity as a function of declination.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    p.add_argument("--dec", type=float, default=-80.0,
                   help='declination in degrees')
    p.add_argument("--index", type=float, default=2.0,
                   help='spectral index')
    p.add_argument("--systematic", help='Systematic to test.')
    p.add_argument("--year", help='Data year.')
    args = p.parse_args()

    # Initialization of multi-year LLH object.
    exp, mc, livetime, ps_llh = load_systematic_dataset('point_source', args.systematic,
                                                        ncpu=args.ncpu, seed=args.seed,
                                                        year=args.year)

    inj= PointSourceInjector(args.index, E0=10**6,
                             sinDec_bandwidth=np.sin(np.radians(2)))
    inj.fill(np.radians(args.dec), exp, mc, livetime)

    result = ps_llh.weighted_sensitivity([0.5, 2.87e-7], [0.9, 0.5],
                                         inj=inj,
                                         eps=1.e-2,
                                         n_bckg=10000,
                                         n_iter=1000,
                                         src_ra=np.pi,
                                         src_dec=np.radians(args.dec))

    flux = np.empty((1,), dtype=[('dec', np.float), ('sens', np.float),
                                 ('disc', np.float)])
    flux['dec'] = args.dec
    flux['sens'] = result[0]['flux'][0]
    flux['disc'] = result[0]['flux'][1]

    np.save(prefix+'systematics/sens_jobs/{}/index_{}/{}_dec_{}.npy'.format(args.year, args.index, args.systematic, args.dec),
            flux)
