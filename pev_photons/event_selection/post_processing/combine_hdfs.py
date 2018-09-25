#!/usr/bin/env python

########################################################################
# Combine HDF files of a dataset into a single Pandas dataframe.
########################################################################

import os
import argparse
import numpy as np
import pandas as pd
from glob import glob

from pev_photons import utils

def get_weights(MC_dataset, energy, nstations):
    """ Create the MC weights for the given dataset generation parameters """

    def norm(emin, emax, eslope):
        #Function from weighting project
        if eslope < -1:
            g = eslope+1
            return (emax**g - emin**g)/g
        else:
            return np.log(emax/emin)

    def int_area(E, theta_max):
        #Integrated Area times Solid Angle
        radius = (800 * np.greater_equal(E, 1e5)
                  + 300 * np.greater_equal(E, 1e6)
                  + 300 * np.greater_equal(E, 1e7))

        return ((radius*100)**2)*(1-np.cos(np.radians(theta_max))**2)*np.pi**2

    events = np.load('/data/user/zgriffith/sim_files/'+MC_dataset+'_events.npy')

    def n_thrown(E):
        # Number of thrown events in an Ebin, normed by the size of the Ebin
        indices = np.floor(10 * np.log10(E)) - 50
        if MC_dataset == '12622':
            return 6e4/norm(1e6, 10**6.1, -1)
        else:
            return np.take(events, indices.astype('int'))/norm(1e6, 10**6.1, -1)

    #Maximum Zenith Angle
    if MC_dataset in ['7006', '7007']:
        max_zen = 40.
    elif MC_dataset in ['12360', '12362']:
        max_zen = 65.
    else:
        max_zen = 45.

    weights = int_area(energy,max_zen)*energy/n_thrown(energy)

    if MC_dataset == '12622':
        prescale = 2. * (np.less(nstations, 8) & np.greater(nstations, 3)) + 1.
        return weights/prescale
    else:
        return weights

def set_to_names(dataset):
    """ Return the file names corresponding to a given dataset. """
    if dataset is not None:
        if dataset in ['12533', '12612', '12613', '12614', '12622']:
            return dataset, 'gamma_mc'
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

        # Event ID info
        series_dict['time'] = store.select('I3EventHeader').time_start_mjd
        series_dict['run'] = store.select('I3EventHeader').Run
        series_dict['event'] = store.select('I3EventHeader').Event
        series_dict['subevent'] = store.select('I3EventHeader').SubEvent

        # Quality cuts independent of reconstruction.
        for cut in cut_keys:
            series_dict[cut] = store['IT73AnalysisIceTopQualityCuts'][cut]

        llh_keys = ['LLH_Ratio', 'LLH_Gamma_q_r', 'LLH_Gamma_q_t', 'LLH_Gamma_t_r',
                    'LLH_Hadron_q_r', 'LLH_Hadron_q_t', 'LLH_Hadron_t_r']
        for key in llh_keys:
            series_dict[key] = store['Laputop_IceTopLLHRatio'][key]

        #---- Separation ----#
        #---- IceTop ----#
        llh_name = 'Laputop_IceTopLLHRatio'
        series_dict['llh_ratio'] = store.select(llh_name).LLH_Ratio
        series_dict['llh_ratio_q_r'] = store.select(llh_name).LLH_Gamma_q_r/store.select(llh_name).LLH_Hadron_q_r
        series_dict['llh_ratio_q_t'] = store.select(llh_name).LLH_Gamma_q_t/store.select(llh_name).LLH_Hadron_q_t
        series_dict['llh_ratio_t_r'] = store.select(llh_name).LLH_Gamma_t_r/store.select(llh_name).LLH_Hadron_t_r

        #---- IceCube ----#
        series_dict['twc_hlc_count'] = store.select('hlc_count_TWC').value
        series_dict['twc_slc_count'] = store.select('slc_count_TWC').value
        series_dict['twc_nchannel'] = store.select('nchannel_TWC').value
        series_dict['twc_hlc_charge'] = store.select('hlc_charge_TWC').value
        series_dict['twc_slc_charge'] = store.select('slc_charge_TWC').value

        try:
            series_dict['srt_hlc_count'] = store.select('all_hlcs_SRTCoincPulses').value
            series_dict['srt_slc_count'] = store.select('all_slcs_SRTCoincPulses').value
            series_dict['srt_nchannel'] = store.select('nchannel_SRTCoincPulses').value
            series_dict['srt_hlc_charge'] = store.select('all_hlc_charge_SRTCoincPulses').value
            series_dict['srt_slc_charge'] = store.select('all_slc_charge_SRTCoincPulses').value
        except:
            series_dict['srt_hlc_count'] = np.zeros(len(series_dict['twc_hlc_count']))
            series_dict['srt_slc_count'] = np.zeros(len(series_dict['twc_hlc_count']))
            series_dict['srt_nchannel'] = np.zeros(len(series_dict['twc_hlc_count']))
            series_dict['srt_hlc_charge'] = np.zeros(len(series_dict['twc_hlc_count']))
            series_dict['srt_slc_charge'] = np.zeros(len(series_dict['twc_hlc_count']))

        tr = np.greater(series_dict['srt_hlc_count'], 0)
        series_dict['counts'] = (tr*series_dict['srt_hlc_count']
                                 + tr*series_dict['srt_slc_count']
                                 + np.invert(tr)*series_dict['twc_hlc_count']
                                 + np.invert(tr)*series_dict['twc_slc_count'])
        series_dict['nchannel'] = (tr*series_dict['srt_nchannel']
                                   + np.invert(tr)*series_dict['twc_nchannel'])
        series_dict['charges'] = (tr*series_dict['srt_hlc_charge']
                                  + tr*series_dict['srt_slc_charge']
                                  + np.invert(tr)*series_dict['twc_hlc_charge']
                                  + np.invert(tr)*series_dict['twc_slc_charge'])

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
            series_dict[reco+'_inice_FractionContainment'] = store[reco+'_inice_FractionContainment']['value']

            if MC_dataset:
                series_dict[reco+'_opening_angle'] = store[reco+'_opening_angle']['value']
                series_dict[reco+'_core_diff'] = np.sqrt((series_dict[reco+'_x'] - series_dict['true_x'])**2 +
                                                         (series_dict[reco+'_y'] - series_dict['true_y'])**2)

    df = pd.DataFrame(series_dict)
    return df.loc[np.isfinite(df['LLH_Ratio'].values)]

def split_sample(df, processing, year):
    """ Split the MC dataset into training/testing and validation samples.
    Parameters
    ----------
    df : Pandas dataframe
        dataframe containing MC events.
    processing : str
        type of event processing.  For training, 80% of events are retained.
    year : str
        Detector year used for MC simulation.

    Returns
    -------
    Pandas dataframe containing only events
    to store for the given processing.
    """

    event_path = utils.resource_dir+'/validation_mc_events/{}'.format(year)
    val_x = np.loadtxt(event_path+'_x.txt')
    val_y = np.loadtxt(event_path+'_y.txt')
    in_val = (np.in1d(df['true_x'].values, val_x)
              & np.in1d(df['true_y'].values, val_y))
    if processing == 'training':
        return df[~in_val]
    else:
        return df[in_val]

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

    pre = os.path.join(utils.prefix, 'datasets', args.processing)
    file_list = glob('{}/post_processing/{}/{}/*.hdf5'.format(pre, args.year, set_name))
    out_file = '{}/dataframes/{}/{}.hdf5'.format(pre, args.year, file_name)

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
    else:
        frames = []
        for i, input_file in enumerate(file_list):
            frames.append(extract_dataframe(input_file, args.MC_dataset,
                                            processing=args.processing))
        df = pd.concat(frames)

    if args.MC_dataset:
        df = split_sample(df, args.processing, args.year)

    with pd.HDFStore(out_file, mode='w') as output_store:
        output_store.append('dataframe', df,
                            format='table', data_columns=True,
                            min_itemsize=30)
