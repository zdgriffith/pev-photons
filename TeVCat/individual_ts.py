#!/usr/bin/env python

########################################################################
# Calculates the true TS for each HESS source
########################################################################

import argparse
import numpy as np

from pev_photons.load_datasets import load_ps_dataset
from pev_photons.support import prefix

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test HESS positions individually',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--outFile', type = str,
                   default='hess_sources_fit_results',
                   help='file name')
    p.add_argument('--extended', action='store_true', default=False,
                   help='If True, use source extension in fit.')
    args = p.parse_args()

    # Load the dataset.
    ps_llh = load_ps_dataset(args)

    sources   = np.load(prefix+'TeVCat/hess_sources.npz')

    fit_arr = np.empty((len(sources['dec']),),
                       dtype=[('TS', np.float), ('nsources', np.float),
                              ('gamma', np.float)])
    
    for i, dec in enumerate(sources['dec']):
    
        if args.extended:
            out = psllh.fit_source(np.radians(sources['ra'][i]),
                                   np.radians(dec),
                                   src_extension=np.radians(sources['extent'])[i],
                                   scramble = False)
        else:
            out = psllh.fit_source(np.radians(sources['ra'][i]),
                                   np.radians(dec),
                                   scramble = False)

        fit_arr['TS'][i] = out[0]
        fit_arr['gamma'][i] = out[1]['gamma']
        fit_arr['nsources'][i] = out[1]['nsources']

    if args.extended:
        np.save(prefix+'TeVCat/extended/'+args.outFile+'.npy', fit_arr)
    else:
        np.save(prefix+'TeVCat/'+args.outFile+'.npy', fit_arr)
