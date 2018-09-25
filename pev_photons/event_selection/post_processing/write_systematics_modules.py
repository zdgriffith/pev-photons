#!/usr/bin/env python

########################################################################
# Write Skylab modules for systematics datasets.
########################################################################

import numpy as np
import pandas as pd
from scipy import stats

from pev_photons import utils

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


def construct_arr(mc_quality, mc, reco='Laputop', isMC=False, testing_fraction=1):
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
        s_arr['ow'] = mc['weights']/testing_fraction
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
    mc_sets = {'2011':'12622', '2012':'12533',
               '2013':'12612', '2014':'12613',
               '2015':'12614'}

    # Data and Simulation Systematics
    years = ['2012', '2015']
    dataset = ['mc', 'exp']
    selections = ['ps', 'diffuse']
    recos = ['Laputop', 'LaputopLambdaUp', 'LaputopLambdaDown',
             'LaputopS125Up', 'LaputopS125Down']

    for year in years:
        for data in dataset:
            if data == 'exp':
                events = pd.read_hdf(utils.prefix+'datasets/systematics/{}.hdf5'.format(year))
            else:
                events = pd.read_hdf(utils.prefix+'datasets/systematics/{}.hdf5'.format(mc_sets[year]))
            mc = pd.read_hdf(utils.prefix+'datasets/systematics/{}.hdf5'.format(mc_sets[year]))
            for reco in recos:
                for selection in selections:
                    if selection == 'ps':
                        mask = (events[reco+'_alpha_2.0_score'] > 0.7) | (events[reco+'_alpha_2.7_score'] > 0.7)
                        mc_mask = (mc[reco+'_alpha_2.0_score'] > 0.7) | (mc[reco+'_alpha_2.7_score'] > 0.7)
                    else:
                        mask = (events[reco+'_alpha_3.0_score'] > 0.7)
                        mc_mask = (mc[reco+'_alpha_3.0_score'] > 0.7)
                    final = construct_arr(mc[mc_mask], events[mask], reco=reco, isMC=(data == 'mc'))
                    np.save(utils.prefix+'datasets/systematics/skylab/{}/{}_{}_{}.npy'.format(year, reco, data, selection), final)

    # Simulation only systematics
    systematics = ['s125', 'charges']
    magnitudes = [[1.02, 1.00, 0.98], [1.10, 1.00, 0.90]]
    years = ['2011', '2012', '2013', '2014', '2015']
    for year in years:
        for i, sys in enumerate(systematics):
            for mag in magnitudes[i]:
                for selection in selections:
                    gammas = pd.read_hdf(utils.prefix+'datasets/systematics/sim_only/{}/{}_{:.2f}_quality.hdf5'.format(year, sys, mag))
                    passing_gammas = pd.read_hdf(utils.prefix+'datasets/systematics/sim_only/{}/{}_{:.2f}_{}.hdf5'.format(year, sys, mag, selection))
                    final = construct_arr(gammas, passing_gammas, isMC=True, testing_fraction=0.2)
                    np.save(utils.prefix+'datasets/systematics/skylab/{}/{}_{:.2f}_mc_{}.npy'.format(year, sys, mag, selection), final)

    # Hadronic interaction model systematics
    year = '2012'
    models = ['sybll', 'qgs']
    for selection in selections:
        for j, model in enumerate(models):
            gammas = pd.read_hdf(utils.prefix+'datasets/systematics/hadronic_models/{}/{}_quality.hdf5'.format(year, model))
            passing_gammas = pd.read_hdf(utils.prefix+'datasets/systematics/hadronic_models/{}/{}_{}.hdf5'.format(year, model, selection))

            if model == 'sybll':
                final = construct_arr(gammas, passing_gammas, isMC=True, testing_fraction=0.2)
            else:
                final = construct_arr(gammas, passing_gammas, isMC=True)
            np.save(utils.prefix+'datasets/systematics/skylab/{}/{}_mc_{}.npy'.format(year, model, selection), final)
