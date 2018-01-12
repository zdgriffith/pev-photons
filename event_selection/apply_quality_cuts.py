#!/usr/bin/env python

########################################################################
# Apply quality cuts to level 3 processed files
########################################################################

import argparse
import numpy as np
import pandas as pd

from pev_photons.support import prefix

def apply_cuts(args, dataset):

    # Load given dataset
    f = pd.read_hdf(prefix+'datasets/level3/'+dataset+'.hdf5')

    # Event must be contained within IceTop
    cut = np.less_equal(f['laputop_it'].values, 1)

    # Within zenith region where reconstruction is verified
    cut = cut&np.less_equal(f['laputop_zen'].values, np.arccos(0.8))

    # Minimum S125 to ensure data/mc agreement
    cut = cut&np.greater(f['s125'].values, 10**(-0.25))

    # Ensure IceTop LLH Ratio succeeded
    cut = cut&np.isfinite(f['llh_ratio'].values)

    # Data files already have basic cuts applied to reduce file size
    if 'mc' in dataset:
        # Standard IceTop cuts for reconstruction quality
        cut = cut&f['standard_filter_cut'].values
        cut = cut&f['beta_cut'].values
        cut = cut&f['laputop_cut'].values
        cut = cut&f['Q_cut'].values
        cut = cut&f['loudest_cut'].values
        cut = cut&np.greater_equal(f['Nstations'].values,5)

    # Apply cuts to data
    cut = np.equal(cut,1)
    f[cut].to_hdf(prefix+'datasets/level3/'+dataset+'_quality.hdf5',
             'dataframe', mode='w')

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='apply quality cuts to level 3 files',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', default='all',
                   help='Year of mc and data. If all, run all years')
    args = p.parse_args()

    for end in ['_mc', '_exp']:
        if args.year == 'all':
            for year in ['2011','2012','2013','2014','2015']:
                apply_cuts(args, year+end)
        else:
            apply_cuts(args, args.year+end)
