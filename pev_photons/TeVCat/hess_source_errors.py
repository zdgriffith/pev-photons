#!/usr/bin/env python

########################################################################
# Calculates the true TS for each HESS source
########################################################################

import time
import argparse
import numpy as np

from pev_photons.utils.load_datasets import load_dataset
from pev_photons.utils.support import prefix, resource_dir

def error_profile(llh, ra, dec, fit, **kwargs):

    t0 = time.time()
    p  = list(kwargs.keys())[0]

    val = llh.scan(ra, dec, fixed=p, **kwargs)
    val = val[val['TS'] >= fit['TS'] - 1]
    val.sort(order=p)

    Min = val[ 0]
    Max = val[-1]

    dMin = fit[p] - Min[p]
    dMax = Max[p] - fit[p]

    print("\n Range for '%s':" % p)
    print("   - min %.2f (TS %.2f)" % (Min[p], Min['TS']))
    print("   - max %.2f (TS %.2f)" % (Max[p], Max['TS']))
    print("   - fit %.2f (-%.2f/+%.2f)" % (fit[p], dMin, dMax))
    print("   - completed in %.2f sec" % (time.time() - t0))
    return [fit[p], dMin, dMax]

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test HESS positions individually',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--outFile', type = str,
                   default='hess_sources_fit_results',
                   help='file name')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    # Load the dataset.
    ps_llh = load_dataset('point_source', ncpu=args.ncpu, seed=args.seed)

    sources = np.load(resource_dir+'hess_sources.npz')

    fit_arr = np.empty((len(sources['dec']),),
                       dtype=[('TS', np.float), ('nsources', np.float),
                              ('gamma', np.float)])
    
    source_fits = {}
    for i, dec in enumerate(sources['dec']):
        source_fits[sources['name'][i]] = {}
        ra = np.radians(sources['ra'][i])
        dec = np.radians(dec)

        TS, xmin = ps_llh.fit_source(ra, dec, scramble=False)
        fit = dict({'TS':TS}, **xmin) 
        source_fits[sources['name'][i]]['gamma'] = error_profile(ps_llh, ra, dec, fit, gamma=np.arange(0.99, 4.01, 0.01))
        source_fits[sources['name'][i]]['nsources'] = error_profile(ps_llh, ra, dec, fit, nsources=np.arange(0, 100, 0.1))
    np.save(prefix+'/TeVCat/fit_uncertainties.npy', source_fits)
