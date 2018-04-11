#!/usr/bin/env python

########################################################################
# 
########################################################################

import numpy as np
import pandas as pd
from scipy import stats

from pev_photons.utils.support import prefix
from icecube import astro

def sigma(y):
    values, base = np.histogram(y, bins = np.arange(0,20,0.01), weights = np.divide(np.ones(len(y)), float(len(y))))
    cumulative = np.cumsum(values)

    for i, val in enumerate(cumulative):
        if val >= 0.68:
            return base[i]/1.51
     
def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

def error(df, mc_quality, x, x_bins, reco):

    bin_size = x_bins[1]-x_bins[0]

    bin_sigmas, bin_edges, n = stats.binned_statistic(np.log10(mc_quality[x]),
                                                      np.degrees(mc_quality[reco+'_opening_angle']),
                                                      statistic=sigma,
                                                      bins=x_bins)
    vals = np.log10(df[x])

    bin_center = bin_edges[:-1] + bin_size/2.
    sigmas = []
    for val in vals:
        sigmas.append(bin_sigmas[find_nearest(bin_center, val)]) 
    
    return np.radians(sigmas)


def construct_arr(mc_quality, mc, reco, isMC=False):
    """ Construct correctly formated data for Skylab """
    if isMC:
        s_arr = np.empty((len(mc['Laputop_E']), ), dtype=[("ra", np.float), ("sinDec", np.float),
                                                          ("dec", np.float),
                                                          ("sigma", np.float), ("logE", np.float),
                                                          ("trueRa", np.float), ("trueDec", np.float),
                                                          ("trueE", np.float), ("ow", np.float)])
        s_arr['trueDec'] = mc['primary_zen'] - np.pi/2.
        s_arr['trueRa'] = mc['primary_azi'] 
        s_arr['trueE'] = mc['primary_E']
        s_arr['ow'] = mc['weights']
    else:
        s_arr = np.empty((len(mc['Laputop_E']), ), dtype=[("ra", np.float), ("sinDec", np.float),
                                                          ("dec", np.float),
                                                          ("sigma", np.float), ("logE", np.float)])

    s_arr['dec'] = mc[reco+'_zenith'] - np.pi/2.
    s_arr['sinDec'] = np.sin(s_arr['dec']) 
    s_arr['ra'] = mc[reco+'_azimuth']
    s_arr['logE'] = np.log10(mc[reco+'_E'])

    s_arr['sigma'] = error(mc, mc_quality, reco+'_E', np.arange(5.5, 8.5, 0.05), reco)

    return s_arr

if __name__ == "__main__":

    years = ['2012']
    dataset = ['mc', 'data']
    selections = ['ps', 'gal']
    recos = ['Laputop', 'LaputopLambdaUp', 'LaputopLambdaDown',
             'LaputopS125Up', 'LaputopS125Down']
    #mc_quality = pd.read_hdf(prefix+'datasets/systematics/hadronic_models/2012_sybll_quality.hdf5')

    for year in years: 
        for data in dataset:
            if data == 'data':
                events = pd.read_hdf(prefix+'datasets/systematics/{}.hdf5'.format(year))
            else:
                events = pd.read_hdf(prefix+'datasets/systematics/{}.hdf5'.format('12533'))
            mc = pd.read_hdf(prefix+'datasets/systematics/{}.hdf5'.format('12533'))
            for reco in recos:
                print(reco)
                for selection in selections:
                    if selection == 'ps':
                        mask = (events[reco+'_alpha_2.0_score'] > 0.7) | ( events[reco+'_alpha_2.7_score'] > 0.7 )
                        mc_mask = (mc[reco+'_alpha_2.0_score'] > 0.7) | (mc[reco+'_alpha_2.7_score'] > 0.7 )
                    else:
                        mask = (events[reco+'_alpha_3.0_score'] > 0.7)
                        mc_mask = (mc[reco+'_alpha_3.0_score'] > 0.7)
                    final = construct_arr(mc[mc_mask], events[mask], reco, isMC=(data == 'mc'))
                    np.save(prefix+'datasets/systematics/skylab/{}_{}_{}_{}.npy'.format(year, data, reco, selection), final)
