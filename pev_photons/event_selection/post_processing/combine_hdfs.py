#!/usr/bin/env python

########################################################################
# Combine HDF files of a dataset into a single Pandas dataframe.
########################################################################

import argparse
import glob
import numpy as np
import pandas as pd

from pev_photons.utils.support import prefix
from pev_photons.event_selection.post_processing.pandas_writer import get_weights

def extract_dataframe(input_file, isMC, systematics=None):
    with pd.HDFStore(input_file, mode='r') as store:
        series_size = store.get_storer('NStation').nrows
        # Dictionary of key: pd.Series pairs to get converted to pd.DataFrame
        series_dict = {}

        value_keys = ['NStation']
        mc_keys = ['zenith', 'azimuth', 'energy']
        cut_keys = []
        lap_keys = ['zenith', 'azimuth']
        lap_cut_keys = []
        lap_param_keys = ['s125']
        if args.complete:
            value_keys += ['IceTopMaxSignal', 'StationDensity']
            mc_keys += ['x', 'y', 'type']
            cut_keys += ['IceTopMaxSignalAbove6', 'IceTopMaxSignalInside',
                         'IceTopNeighbourMaxSignalAbove4',
                         'IceTop_StandardFilter', 'StationDensity_passed']
            lap_cut_keys += ['fit_status', 'containment_cut', 'zenith_cut',
                             's125_cut', 'beta_cut']
            lap_keys += ['x', 'y', 'fit_status']
            lap_param_keys += ['beta', 'age', 'xc_err', 'yc_err', 'ny_err',
                               'nx_err', 'tc_err', 'log10_s125_err', 'beta_err',
                               's50', 's70', 's80', 's100', 's150', 's180', 's250',
                               's500', 'e_proton', 'e_iron', 'e_h4a', 'llh',
                               'llh_silent', 'chi2', 'chi2_time',
                               'ndf', 'rlogl', 'nmini']

        for key in value_keys:
            series_dict[key] = store[key]['value']

        if isMC:
            for key in mc_keys:
                series_dict['MC_{}'.format(key)] = store['MCPrimary'][key]

        series_dict['weights'] = get_weights(args.dataset, series_dict['MC_energy'], series_dict['NStation'])

        # Quality cuts independent of reconstruction.
        for cut in cut_keys:
            series_dict[cut] = store['IT73AnalysisIceTopQualityCuts'][cut]

        llh_keys = ['LLH_Ratio', 'LLH_Gamma_q_r', 'LLH_Gamma_q_t', 'LLH_Gamma_t_r',
                    'LLH_Hadron_q_r', 'LLH_Hadron_q_t', 'LLH_Hadron_t_r']
        for key in llh_keys:
            series_dict[key] = store['Laputop_IceTopLLHRatio'][key]

        recos = ['Laputop']
        if systematics:
            recos.extend(['LaputopLambdaUp', 'LaputopLambdaDown',
                          'LaputopS125Up', 'LaputopS125Down'])
        for i, reco in enumerate(recos):
            laputop = store[reco]
            laputop_params = store[reco+'Params']

            for key in lap_keys:
                series_dict[reco+'_{}'.format(key)] = laputop[key]
            for key in lap_param_keys:
                series_dict[reco+'_{}'.format(key)] = laputop_params[key]
            for cut in lap_cut_keys:
                series_dict[reco+'_'+cut] = store[reco+'_quality_cuts'][cut]
            
            series_dict[reco+'_opening_angle'] = store[reco+'_opening_angle']['value']
            series_dict[reco+'_log10_s125'] = np.log10(series_dict[reco+'_s125'])
            series_dict[reco+'_energy'] = store[reco+'_E']['value']

            if args.complete:
                series_dict[reco+'_FractionContainment'] = store[reco+'_FractionContainment']['value']
                series_dict[reco+'_core_diff'] = np.sqrt((series_dict[reco+'_x'] - series_dict['MC_x'])**2 +
                                                         (series_dict[reco+'_y'] - series_dict['MC_y'])**2)

    df = pd.DataFrame(series_dict)

    return df

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Rewrite HDF files for analysis purposes',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dataset', help='Set to run over')
    p.add_argument('--isMC', action="store_true", default=False,
                   help='Is this simulation?')
    p.add_argument('--complete', action="store_true", default=False,
                   help='Keep much more information.')
    p.add_argument('--training', action="store_true", default=False,
                   help='Training datasets?')
    p.add_argument('--systematics', action="store_true", default=False,
                   help='Include systematics?')
    args = p.parse_args()

    if args.training:
        file_list = glob.glob(prefix+'/datasets/training/'+args.dataset+'/*.hdf5')
        outFile = prefix+'/datasets/training/'+args.dataset+'.hdf5'
    else:
        file_list = glob.glob(prefix+'/datasets/'+args.dataset+'/*.hdf5')
        outFile = prefix+'/datasets/'+args.dataset+'.hdf5'

    with pd.HDFStore(outFile, mode='w') as output_store:
        for i, input_file in enumerate(file_list):
            print(i)
            df = extract_dataframe(input_file, args.isMC,
                                   systematics=args.systematics)
            output_store.append('dataframe', df, format='table',
                                data_columns=True, min_itemsize=30)
