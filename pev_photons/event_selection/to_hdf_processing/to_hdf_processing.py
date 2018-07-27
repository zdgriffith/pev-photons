#!/usr/bin/env python

########################################################################
# Run analysis-level processing on I3 Files, store as HDF Files
########################################################################

import argparse
import os
import sys
import copy
import numpy as np

from sklearn.externals import joblib
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, phys_services, toprec
from icecube import coinc_twc, static_twc, SeededRTCleaning
from icecube.tableio import I3TableWriter
from icecube.hdfwriter import I3HDFTableService
from icecube.recclasses import I3LaputopParams, LaputopParameter
from icecube.icetop_Level3_scripts.functions import count_stations 
from icecube.frame_object_diff.segments import uncompress

from pev_photons.event_selection.llh_ratio_scripts.llh_ratio_i3_module import IceTop_LLH_Ratio
from pev_photons.event_selection.icecube_cleaning import icecube_cleaning
from pev_photons.event_selection.run_laputop import run_laputop
from pev_photons.utils.support import resource_dir

def select_keys(isMC=False, store_extra=False, recos=['Laputop']):
    """ Determine which keys get stored in the HDF file. """

    # Keep these no matter what.
    keys = ['I3EventHeader', 'charges', 'IceTopLLHRatio']

    # Reconstruction related keys.
    reco_keys = ['', 'Params', '_FractionContainment',
                 '_inice_FractionContainment', '_E',
                 '_IceTopLLHRatio', '_opening_angle',
                 '_quality_cuts', '_passing']
    for reco in recos:
        keys += [reco+key for key in reco_keys]
        for alpha in [2.0, 2.7, 3.0]:
            keys += [reco+'_alpha_{}_score'.format(alpha)]

    if isMC:
        keys += ['MCPrimary', 'MCPrimaryInfo',
                 'MCPrimary_inice_FractionContainment',
                 'MCPrimary_FractionContainment']

    if store_extra:
        # Information not necessary for the final analysis.
        keys += ['IT73AnalysisIceTopQualityCuts',
                 'IceTopMaxSignal', 'StationDensity',
                 'IceTopNeighbourMaxSignal', 'hlc_count_TWC',
                 'slc_count_TWC','nchannel_TWC', 'hlc_charge_TWC',
                 'slc_charge_TWC', 'mjd_time', 'NStation']

        for pulsename in ['SRTCoincPulses', 'InIcePulses', 'CoincPulses']:
            keys += ['all_hlcs_'+pulsename, 'all_slcs_'+pulsename,
                     'all_hlc_charge_'+pulsename,
                     'all_slc_charge_'+pulsename,
                     'nchannel_'+pulsename]
    return keys


def base_quality_cuts(frame):
    """ Calculate quality cuts """
    keys = ['IceTopMaxSignalAbove6', 'IceTopMaxSignalInside',
            'IceTopNeighbourMaxSignalAbove4',
            'IceTop_StandardFilter', 'StationDensity_passed']
    cuts = frame['IT73AnalysisIceTopQualityCuts']
    quality_cuts = dataclasses.I3MapStringBool()
    for key in keys:
        quality_cuts[key] = cuts[key]

    if 'IceTopHLCSeedRTPulses' in frame:
        nstation = count_stations(dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'IceTopHLCSeedRTPulses')) 
        if 'NStation' not in frame:
            frame.Put('NStation', icetray.I3Int(nstation))
        quality_cuts['NStation_cut'] = (frame['NStation'] >= 5)
    else:
        quality_cuts['NStation_cut'] = False

    return np.all(quality_cuts.values())


def reco_quality_cuts(frame, reco='Laputop'):
    """ Calculate quality cuts using the given reconstruction """
    quality_cuts = dataclasses.I3MapStringBool()

    quality_cuts['fit_status'] = (frame[reco].fit_status_string == 'OK')
    quality_cuts['containment_cut'] = (frame[reco+'_FractionContainment'] < 1.0)

    laputop = frame[reco]
    laputop_params = frame[reco+'Params']

    quality_cuts['zenith_cut'] = (laputop.dir.zenith < float(np.arccos(0.8)))

    params = I3LaputopParams.from_frame(frame, reco+'Params')
    log_S125 = params.value(LaputopParameter.Log10_S125)
    quality_cuts['s125_cut'] = (log_S125 > -0.25)
    quality_cuts['beta_cut'] = (params.value(LaputopParameter.Beta) > 1.4) & (params.value(LaputopParameter.Beta) < 9.5)

    frame.Put(reco+'_quality_cuts', quality_cuts)
    frame.Put(reco+'_passing', icetray.I3Bool(bool(np.all(quality_cuts.values()))))


def calculate_containment(frame, particle='Laputop'):
    """ Calculate geometry containment values using Kath's method. """

    scaling = phys_services.I3ScaleCalculator(frame['I3Geometry'])
    if particle in frame:
        if particle+'_FractionContainment' not in frame:
            frame.Put(particle+'_FractionContainment',
                      dataclasses.I3Double(scaling.scale_icetop(frame[particle])))
        if particle+'_inice_FractionContainment' not in frame:
            frame.Put(particle+'_inice_FractionContainment',
                      dataclasses.I3Double(scaling.scale_inice(frame[particle])))


def opening_angle(frame, reco='Laputop'):
    """ Calculate the opening angle for a given reconstruction. """

    lap_zen = frame[reco].dir.zenith
    lap_azi = frame[reco].dir.azimuth
    mc_zen = frame['MCPrimary'].dir.zenith
    mc_azi = frame['MCPrimary'].dir.azimuth

    par = {}
    for key in [reco, 'MCPrimary']:
        par[key] = {'x': np.sin(frame[key].dir.zenith)*np.cos(frame[key].dir.azimuth),
                    'y': np.sin(frame[key].dir.zenith)*np.sin(frame[key].dir.azimuth),
                    'z': np.cos(frame[key].dir.zenith)}

    opening_angle = np.arccos(par[reco]['x']*par['MCPrimary']['x']
                              + par[reco]['y']*par['MCPrimary']['y']
                              + par[reco]['z']*par['MCPrimary']['z'])

    frame.Put(reco+'_opening_angle', dataclasses.I3Double(opening_angle))


def laputop_energy(frame, reco='Laputop'):
    """ Convert Laputop S125 to energy based on cosmic-ray simulation studies. """
    params = I3LaputopParams.from_frame(frame, reco+'Params')
    s125 = 10 ** params.value(LaputopParameter.Log10_S125)

    coszen=np.cos(frame[reco].dir.zenith)

    if coszen > 0.95 and coszen <= 1.:
        mixed_energy= 0.933316*np.log10(s125) + 6.010569
    elif coszen > 0.9 and coszen <= 0.95:
        mixed_energy= 0.923860*np.log10(s125) + 6.054677
    elif coszen > 0.85 and coszen <= 0.9:
        mixed_energy= 0.914971*np.log10(s125) + 6.109777
    elif coszen > 0.8 and coszen <= 0.85:
        mixed_energy= 0.907456*np.log10(s125) + 6.177271
    else:
        mixed_energy= np.nan

    frame.Put(reco+'_E' , dataclasses.I3Double(10**mixed_energy))


def shift_s125(frame, shift=0.03):
    """ Makes new reconstructions that only differ from the standard
        by a shift in S125. """
    recos = ['LaputopS125Down', 'LaputopS125Up']
    for i, ratio in enumerate([1-shift, 1+shift]):
        params = I3LaputopParams.from_frame(frame, 'LaputopParams')
        shift_params = copy.deepcopy(params)
        shift_params.set_value(LaputopParameter.Log10_S125,
                               np.log10(ratio*10**params.value(LaputopParameter.Log10_S125)))

        frame[recos[i]+'Params'] = shift_params
        frame[recos[i]] = frame['Laputop']


def calculate_inice_charge(frame):
    """ Calculates the total charge deposited in IceCube. """
    if frame.Has('SRTCoincPulses'):
        # If the event had an IceCube trigger, use the SeededRT pulses
        # to determine the charge feature.  Otherwise, use the
        # optimized cleaning described in the wiki.
        trigger = np.greater(frame['all_hlcs_SRTCoincPulses'],0)
        charges = (trigger*(frame['all_hlc_charge_SRTCoincPulses'].value
                            + frame['all_slc_charge_SRTCoincPulses'].value)
                   + np.invert(trigger)*(frame['hlc_charge_TWC'].value
                                         + frame['slc_charge_TWC'].value))
    else:
        # If there are no events in a file with SeededRT applied, all
        # charges come from the optimized cleaning.
        charges = frame['hlc_charge_TWC'].value + frame['slc_charge_TWC'].value

    frame['charges'] = dataclasses.I3Double(charges)


def apply_random_forest(frame, random_forests, isMC=False, reco='Laputop'):
    """ Calculates Random Forest scores. """
    if not frame[reco+'_passing']:
        for alpha in ['2.0', '2.7', '3.0']:
            frame[reco+'_alpha_'+alpha+'_score'] = dataclasses.I3Double(0)
        return

    laputop = frame[reco]
    params = I3LaputopParams.from_frame(frame, reco+'Params')
    log_S125 = params.value(LaputopParameter.Log10_S125)

    features = np.array([frame['charges'].value,
                         frame[reco+'_inice_FractionContainment'].value,
                         frame[reco+'_IceTopLLHRatio']['LLH_Ratio'],
                         log_S125, np.sin(laputop.dir.zenith - np.pi/2.)]).T.reshape(1,-1)

    if np.any(np.isnan(features)):
        for alpha in ['2.0', '2.7', '3.0']:
            frame[reco+'_alpha_'+alpha+'_score'] = dataclasses.I3Double(0)
        return
        
    for alpha in ['2.0', '2.7', '3.0']:
        score = random_forests['alpha_'+alpha].predict_proba(features).T[1][0]
        frame['{}_alpha_{}_score'.format(reco, alpha)] = dataclasses.I3Double(score)

def cut_events(frame, recos=[], threshold=0.7):
    """ Cuts all events which are below threshold for all classifiers."""
    for reco in recos:
        for alpha in ['2.0', '2.7', '3.0']:
            if frame['{}_alpha_{}_score'.format(reco, alpha)] > threshold:
                return True
    return False


def main(in_files, out_file, year, isMC=False, systematics=False,
         run_migrad=False, store_extra=False, training=False):
    
    tray = I3Tray()
    tray.AddModule('I3Reader', 'Reader', FilenameList=in_files)
    tray.AddSegment(uncompress, 'uncompress')

    tray.AddModule(base_quality_cuts, 'base_quality_cuts')

    tray.AddSegment(icecube_cleaning, 'icecube_cleaning')
    tray.AddModule(calculate_inice_charge, 'icecube_charge')

    if not training:
        rf = {}
        for alpha in ['2.0', '2.7', '3.0']:
            rf['alpha_'+alpha] = joblib.load('/data/user/zgriffith/rf_models/'+year+'/final/forest_'+alpha+'.pkl')
            rf['alpha_'+alpha].verbose = 0

    recos = ['Laputop']
    if run_migrad:
        tray.AddSegment(run_laputop, 'laputop_migrad', algorithm='MIGRAD',
                        laputop_name='LaputopMigrad')
        recos.append('LaputopMigrad')
    if systematics:
        lambdas = {'2011': 2.1, '2012': 2.25, '2013': 2.25,
                   '2014': 2.3, '2015': 2.3}
        tray.AddSegment(run_laputop, 'laputop_lambda_up',
                        lambda_val=lambdas[year]+0.2,
                        laputop_name='LaputopLambdaUp')
        tray.AddSegment(run_laputop, 'laputop_lambda_down',
                        lambda_val=lambdas[year]-0.2,
                        laputop_name='LaputopLambdaDown')
        tray.AddModule(shift_s125, 'shift_s125')
        recos.extend(['LaputopLambdaUp', 'LaputopLambdaDown',
                      'LaputopS125Up', 'LaputopS125Down'])

    for reco in recos:
        tray.AddModule(calculate_containment, 'containment_'+reco,
                       particle=reco)
        tray.AddModule(reco_quality_cuts, 'quality_cuts_'+reco, reco=reco)
        tray.AddModule(laputop_energy, 'reco_energy_'+reco, reco=reco)
        tray.AddModule(IceTop_LLH_Ratio, 'IceTop_LLH_ratio_'+reco)(
                       ('Track', reco), ('Output', reco+'_IceTopLLHRatio'),
                       ('TwoDPDFPickleYear', year),
                       ('GeometryHDF5', resource_dir+'/geometry.h5'),
                       ('checkQuality', True),
                       ('highEbins', True))
        tray.AddModule(apply_random_forest, 'apply_random_forest_'+reco,
                       random_forests=rf, reco=reco)
        if isMC:
            tray.AddModule(opening_angle, 'opening_angle_'+reco, reco=reco)

    if isMC:
        tray.AddModule(calculate_containment, 'True_containment',
                       particle='MCPrimary')
    else:
        tray.AddModule(cut_events, 'cut_events',
                       recos=recos)

    # Write events to an HDF file
    keys = select_keys(isMC=isMC, store_extra=store_extra, recos=recos)
    hdf = I3HDFTableService(out_file)
    tray.AddModule(I3TableWriter, tableservice=hdf,
                   keys=keys, SubEventStreams=['ice_top'])

    tray.AddModule('TrashCan', 'Done')
    tray.Execute()
    tray.Finish()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--input_files', help='Input file(s)', nargs='*')
    p.add_argument('--output', help='Output file name')
    p.add_argument('--gcdfile', help='The GCD file to be used.')
    p.add_argument('--year', help='dataset year')
    p.add_argument('--isMC', action='store_true', default=False,
                   help='Is this a Monte Carlo dataset?')
    p.add_argument('--run_migrad', action='store_true', default=False,
                   help='Run Laputop with MIGRAD?')
    p.add_argument('--systematics', action='store_true', default=False,
                   help='Process with systematic reconstructions?')
    p.add_argument('--store_extra', action='store_true', default=False,
                   help='Store additional keys in HDF files?')
    p.add_argument('--training', action='store_true', default=False,
                   help='Process training data?')
    args = p.parse_args()

    in_files = [args.gcdfile] + args.input_files
    main(in_files, out_file=args.output, year=args.year, isMC=args.isMC,
         systematics=args.systematics, run_migrad=args.run_migrad,
         store_extra=args.store_extra, training=args.training)
