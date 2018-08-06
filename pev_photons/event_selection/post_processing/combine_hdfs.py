#!/usr/bin/env python

########################################################################
# Combine HDF files of a dataset into a single Pandas dataframe.
########################################################################

import os
import argparse
import numpy as np
import pandas as pd
from glob import glob

from pev_photons.utils.support import prefix
from pev_photons.event_selection.post_processing.pandas_writer import get_weights

def set_to_names(dataset):
    """ Return the file names corresponding to a given dataset. """
    if dataset is not None:
        if dataset in ['12533', '12612', '12613', '12614', '12622']:
            return dataset, 'gammas'
    else:
        return 'data', 'data'

def extract_dataframe(input_file, MC_dataset=None, processing=''):
    """ Given an HDF file, converts the desired fields
        to a Pandas dataframe.
    Parameters
    ----------
    input_file : str
        The name of the HDF file to be converted.
    MC_dataset : str
        The dataset number if MC, "None" if data.
    processing : str, optional
        The type of file processing. Optional categories
        are "systematics" and "training".

    Returns
    -------
    df : Pandas dataframe
    """
   
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

        if processing == 'training':
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

        if MC_dataset:
            for key in mc_keys:
                series_dict['true_{}'.format(key)] = store['MCPrimary'][key]
            series_dict['weights'] = get_weights(MC_dataset, series_dict['true_energy'],
                                                 series_dict['NStation'])

        # Quality cuts independent of reconstruction.
        for cut in cut_keys:
            series_dict[cut] = store['IT73AnalysisIceTopQualityCuts'][cut]

        llh_keys = ['LLH_Ratio', 'LLH_Gamma_q_r', 'LLH_Gamma_q_t', 'LLH_Gamma_t_r',
                    'LLH_Hadron_q_r', 'LLH_Hadron_q_t', 'LLH_Hadron_t_r']
        for key in llh_keys:
            series_dict[key] = store['Laputop_IceTopLLHRatio'][key]

        recos = ['Laputop']
        if processing == 'systematics':
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
            

            series_dict[reco+'_log10_s125'] = np.log10(series_dict[reco+'_s125'])
            series_dict[reco+'_energy'] = store[reco+'_E']['value']
            series_dict[reco+'_FractionContainment'] = store[reco+'_FractionContainment']['value']

            if MC_dataset:
                series_dict[reco+'_opening_angle'] = store[reco+'_opening_angle']['value']
                series_dict[reco+'_core_diff'] = np.sqrt((series_dict[reco+'_x'] - series_dict['true_x'])**2 +
                                                         (series_dict[reco+'_y'] - series_dict['true_y'])**2)
    df = pd.DataFrame(series_dict)

    return df

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Convert processed events to a Pandas dataframe.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', help='Detector year.')
    p.add_argument('--dask', action='store_true', default=False,
                   help='Use Dask to parellelize the processing?')
    p.add_argument('--MC_dataset', default=None,
                   help='If simulation, the dataset to run over.')
    p.add_argument('--processing', choices=['', 'training', 'systematics'],
                   default='', help=('Processing category.'
                                     'Default is for the standard analysis.'))
    args = p.parse_args()

    set_name, file_name = set_to_names(args.MC_dataset)

    pre = os.path.join(prefix, 'datasets', args.processing)
    file_list = glob('{}/post_processing/{}/{}/*.hdf5'.format(pre, args.year, set_name))
    out_file = '{}/pd_dataframes/{}/{}.hdf5'.format(pre, args.year, file_name)

    if args.dask:
        from dask.diagnostics import ProgressBar
        from dask import delayed
        import dask.dataframe as dd
        import dask.multiprocessing
        with ProgressBar():
            delayed_dfs = [delayed(extract_dataframe(input_file, args.MC_dataset,
                                                     processing=args.processing))
                           for input_file in file_list]
            df = dd.from_delayed(delayed_dfs).compute(num_workers=10)
        with pd.HDFStore(out_file, mode='w') as output_store:
            output_store.append('dataframe', df, format='table',
                                data_columns=True, min_itemsize=30)

    else:
        with pd.HDFStore(out_file, mode='w') as output_store:
            for i, input_file in enumerate(file_list):
                print(i)
                df = extract_dataframe(input_file, args.MC_dataset,
                                       processing=args.processing)
                output_store.append('dataframe', df, format='table',
                                    data_columns=True, min_itemsize=30)
