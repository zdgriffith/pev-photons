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
    args = p.parse_args()

    hess = np.load(utils.prefix+'resources/hess_sources.npz')

    # Load the dataset.

    fit_results = np.load(utils.prefix+'/TeVCat/hess_sources_fit_results.npy')
    sens = list()

    for i, alpha in enumerate(hess['alpha']):
        ps_llh = utils.load_dataset('point_source', ncpu=args.ncpu, seed=args.seed,
                                    absorption=hess['distance'][i])
        if np.isnan(alpha):
            sens.append(np.nan)
        else:
            dec = np.radians(hess['dec'][i])
            inj= PointSourceInjector(alpha, E0=2e6,
                                     sinDec_bandwidth=np.sin(np.radians(2)))
            inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)

            s, sens_err = sensitivity_flux(ts=fit_results['TS'][i], p=0.9, llh=ps_llh,
                                           inj=inj, fguess=1e-23, nstep=10,
                                           path='/home/zgriffith/public_html/pev_photons/TeVCat/',
                                           **{'src_ra':np.pi, 'src_dec':dec})
            sens.append(s)
            print(sens)

    a = dict()
    a['name'] = hess['name']
    a['sensitivity'] = sens

    np.savez(utils.prefix+'TeVCat/hess_upper_limits_w_abs.npz', **a)
