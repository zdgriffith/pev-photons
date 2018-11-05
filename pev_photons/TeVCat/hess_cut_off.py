#!/usr/bin/env python

########################################################################
# Calculates the sensitivity to each HESS source's
# declination and spectral index
########################################################################

import argparse
import numpy as np

from skylab.ps_injector import PointSourceInjector
from skylab.sensitivity_utils import sensitivity_flux

from pev_photons import utils

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
    p.add_argument("--Ecut", type=int, default=100,
                   help='Energy cut off in TeV.')
    args = p.parse_args()

    hess = np.load(utils.prefix+'resources/hess_sources.npz')
    # Load the dataset.
    ps_llh = utils.load_dataset('point_source', ncpu=args.ncpu, seed=args.seed,
                                absorption=hess['distance'][args.source])

    fit_results = np.load(utils.prefix+'/TeVCat/hess_sources_fit_results.npy')

    dec = np.radians(hess['dec'][args.source])
    inj= PointSourceInjector(hess['alpha'][args.source], E0=2e6,
                             Ecut=args.Ecut*1e3,
                             sinDec_bandwidth=np.sin(np.radians(2)))
    inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)

    if args.Ecut > 10000:
        flux_i = np.load(utils.prefix+'TeVCat/cut_off/{}_Ecut_{}_sens.npy'.format(args.source, 10000))
    else:
        flux_i = np.load(utils.prefix+'TeVCat/cut_off/{}_Ecut_{}_sens.npy'.format(args.source, args.Ecut))
    sens, sens_err = sensitivity_flux(ts=fit_results['TS'][args.source], p=0.9, llh=ps_llh,
                                      inj=inj, fguess=flux_i, nstep=10,
                                      **{'src_ra':np.pi, 'src_dec':dec})

    np.save(utils.prefix+'TeVCat/cut_off_utils/{}_Ecut_{}_sens.npy'.format(args.source, args.Ecut), sens)

    '''
    result = ps_llh.weighted_sensitivity([0.5, 2.87e-7], [0.9, 0.5],
                                         inj=inj,
                                         eps=1.e-2,
                                         n_bckg=10000,
                                         n_iter=1000,
                                         src_ra=np.pi, src_dec=dec)
    sens = result[0]["flux"][0]
    disc = result[0]["flux"][1]
    np.save(utils.prefix+'TeVCat/cut_off/{}_Ecut_{}_sens.npy'.format(args.source, args.Ecut), sens)
    np.save(utils.prefix+'TeVCat/cut_off/{}_Ecut_{}_disc.npy'.format(args.source, args.Ecut), disc)
    '''
