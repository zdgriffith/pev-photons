#!/usr/bin/env python

########################################################################
# 
########################################################################

import numpy as np
import pandas as pd
from scipy import stats

from pev_photons.utils.support import prefix

def sigma(y):
    values, base = np.histogram(y, bins = np.arange(0,20,0.01), weights = np.divide(np.ones(len(y)), float(len(y))))
    cumulative = np.cumsum(values)

    for i, val in enumerate(cumulative):
        if val >= 0.68:
            return base[i]/1.51
     
def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

def error(df, mc_quality, x, x_bins):

    bin_size = x_bins[1]-x_bins[0]

    if x == 'laputop_E':
        bin_sigmas, bin_edges, binnumber = stats.binned_statistic(np.log10(mc_quality[x]),mc_quality['opening_angle'], statistic = sigma, bins = x_bins)
        vals = np.log10(df[x])
    else:
        bin_sigmas, bin_edges, binnumber = stats.binned_statistic(mc_quality[x],mc_quality['opening_angle'], statistic = sigma, bins = x_bins)
        vals = df[x]

    bin_center = bin_edges[:-1] + bin_size/2.
    sigmas = []
    for val in vals:
        sigmas.append(bin_sigmas[find_nearest(bin_center, val)]) 
    
    return np.radians(sigmas)


def construct_arr(mc_quality, mc, testing_fraction=1):
    """ Construct correctly formated data for Skylab """
    from icecube import astro
    s_arr = np.empty((len(mc['laputop_E']), ), dtype=[("ra", np.float), ("sinDec", np.float),
                                                      ("dec", np.float),
                                                      ("sigma", np.float), ("logE", np.float),
                                                      ("trueRa", np.float), ("trueDec", np.float),
                                                      ("trueE", np.float), ("ow", np.float)])
    s_arr['dec'] = mc['laputop_zen'] - np.pi/2.
    s_arr['sinDec'] = np.sin(s_arr['dec']) 
    s_arr['ra'] = mc['laputop_azi']
    s_arr['logE'] = np.log10(mc['laputop_E'])
    s_arr['sigma'] = error(mc, mc_quality, 'laputop_E', np.arange(5.5, 8.5, 0.05))

    s_arr['trueDec'] = mc['primary_zen'] - np.pi/2.
    s_arr['trueRa'] = mc['primary_azi'] 
    s_arr['trueE'] = mc['primary_E']

    s_arr['ow'] = mc['weights']/testing_fraction

    return s_arr

if __name__ == "__main__":

    years = ['2012']
    models = ['sybll', 'qgs']
    selections = ['ps', 'gal']

    for i, year in enumerate(years): 
        for selection in selections:
            for j, model in enumerate(models):
                gammas = pd.read_hdf(prefix+'datasets/systematics/{}_{}_quality.hdf5'.format(year, model))
                passing_gammas = pd.read_hdf(prefix+'datasets/systematics/{}_{}_{}.hdf5'.format(year, model, selection))
                if model == 'sybll':
                    final = construct_arr(gammas, passing_gammas, testing_fraction=0.2)
                else:
                    final = construct_arr(gammas, passing_gammas)
                np.save(prefix+'datasets/systematics/{}_{}_{}.npy'.format(year, model, selection), final)
                np.save(prefix+'datasets/systematics/{}_{}_{}.npy'.format(year, model, selection), final)