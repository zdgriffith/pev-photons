#!/usr/bin/env python

########################################################################
# Write training and testing files for each MC year of analysis 
########################################################################

import pandas as pd
import numpy as np

from pev-photons.utils.support import prefix

def write_files(year):
    """ write training and testing files for an MC year """

    mc = pd.read_hdf(prefix+'resources/datasets/level3/{}_mc.hdf5'.format(year))

    cut = mc['standard_filter_cut'] & mc['beta_cut'] & mc['laputop_cut']
    cut = cut & mc['Q_cut'] & mc['loudest_cut']
    cut = cut & np.greater_equal(mc['Nstations'],5)
    cut = cut & np.isfinite(mc['llh_ratio'])
    cut = cut & np.less_equal(mc['laputop_zen'], np.arccos(0.8))
    cut = cut & np.less_equal(mc['laputop_it'], 1)
    cut = cut & np.greater_equal(mc['s125'], 10**-0.25)

    np.random.seed(1337)
    training_fraction = 0.8
    is_training = np.random.choice(2, len(mc['laputop_E']),
                                   p=[1 - training_fraction, training_fraction])

    mc[cut&is_training].to_hdf(prefix+'datasets/level3/{}_mc_training.hdf5'.format(year),
                               'dataframe', mode='w')
    mc[cut&~is_training].to_hdf(prefix+'datasets/level3/{}_mc_testing.hdf5'.format(year),
                                'dataframe', mode='w')

if __name__ == "__main__":
    years = ['2011', '2012', '2013', '2014', '2015']
    for year in years:
        write_files(year)
