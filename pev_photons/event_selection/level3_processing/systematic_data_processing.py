#!/usr/bin/env python

########################################################################
# Process Level3 Data files 
########################################################################

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

from pev_photons.event_selection.run_laputop import run_laputop
from pev_photons.event_selection.icecube_cleaning import icecube_cleaning

Par = LaputopParameter
lambdas = {'2011': 2.1, '2012': 2.25, '2013': 2.25,
           '2014': 2.3, '2015': 2.3}

def select_keys(isMC=False):
    it_keys=['I3EventHeader']
    analysis_keys = []
    lap_keys = ['', 'Params', '_FractionContainment',
                '_inice_FractionContainment', '_E',
                '_opening_angle', '_quality_cuts']
    for reco in ['', 'LambdaUp', 'LambdaDown', 'S125Up','S125Down']:
        it_keys += ['Laputop'+reco+key for key in lap_keys]
        analysis_keys += ['Laputop'+reco+'_alpha_2_0_score',
                          'Laputop'+reco+'_alpha_2_7_score',
                          'Laputop'+reco+'_alpha_3_0_score']

    MC_keys=['MCPrimary', 'MCPrimaryInfo',
             'MCPrimary_inice_FractionContainment',
             'MCPrimary_FractionContainment']

    book_keys=it_keys+analysis_keys
    if isMC:
        book_keys+=MC_keys
    return book_keys

def quality_cuts(frame, isMC=False, reco='Laputop'):
    keys = [
            'IceTopMaxSignalAbove6',
            'IceTopMaxSignalInside',
            'IceTopNeighbourMaxSignalAbove4',
            'IceTop_StandardFilter',
            'StationDensity_passed',
           ]
    cuts = frame['IT73AnalysisIceTopQualityCuts']
    quality_cuts = dataclasses.I3MapStringBool()
    for key in keys:
        quality_cuts[key] = cuts[key]

    if 'IceTopHLCSeedRTPulses' in frame:
        nstation = count_stations(dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'IceTopHLCSeedRTPulses')) 
        if 'NStation' not in frame:
            frame.Put('NStation', icetray.I3Int(nstation))
        quality_cuts['NStation_cut'] = frame['NStation'] >= 5
    else:
        quality_cuts['NStation_cut'] = False

    quality_cuts['fit_status'] = frame[reco].fit_status_string == "OK"
    quality_cuts['containment_cut'] = frame[reco+'_FractionContainment'] < 1.0

    laputop = frame[reco]
    laputop_params = frame[reco+'Params']

    quality_cuts['zenith_cut'] = laputop.dir.zenith < float(np.arccos(0.8))

    params = I3LaputopParams.from_frame(frame, reco+'Params')
    s125 = 10 ** params.value(Par.Log10_S125)
    quality_cuts['s125_cut'] = s125 > 10**-0.25
    quality_cuts['beta_cut'] = (params.value(Par.Beta) > 1.4) & (params.value(Par.Beta) < 9.5)

    frame.Put(reco+'_quality_cuts', icetray.I3Bool(bool(np.all(quality_cuts.values()))))

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

    return

def laputop_energy(frame, reco='Laputop'):

    if not frame[reco+'_quality_cuts']:
        frame.Put(reco+"_E" , dataclasses.I3Double(np.nan))
    else:
        params = I3LaputopParams.from_frame(frame, reco+'Params')
        s125 = 10 ** params.value(Par.Log10_S125)

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

        frame.Put(reco+"_E" , dataclasses.I3Double(10**mixed_energy))

    return

def count_icetop_stations(frame):
    """ Count the number of stations hit in IceTop """

    if 'IceTopHLCSeedRTPulses' in frame:
        nstation = count_stations(dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'IceTopHLCSeedRTPulses')) 
        frame.Put('NStation', icetray.I3Int(nstation))

    return 

def cut_small(frame):
    """ Ensure small events are removed. """

    if frame['NStation'] < 5:
        return False
    elif not frame.Has('IceTopLaputopSeededSelectedSLC'):
        return False
    return 

def shift_s125(frame):
    """make new reconstructions that only differ from the standard
       by a shift in S125"""

    recos = ['LaputopS125Down', 'LaputopS125Up']
    for i, ratio in enumerate([0.97, 1.03]):
        params = I3LaputopParams.from_frame(frame, 'LaputopParams')
        shift_params = copy.deepcopy(params)
        shift_params.set_value(Par.Log10_S125,
                               np.log10(ratio*10**params.value(Par.Log10_S125)))

        frame[recos[i]+'Params'] = shift_params
        frame[recos[i]] = frame['Laputop']

def apply_random_forest(frame, random_forests, isMC=False, reco='Laputop'):
    if not frame[reco+'_quality_cuts']:
        for index in ['2_0','2_7','3_0']:
            frame[reco+'_alpha_'+index+'_score'] = dataclasses.I3Double(0)
    else:
        feats = ['charges', 'laputop_ic', 'llh_ratio',
                 's125', 'laputop_zen']
        f = {}

        # Determining the total charge in IceCube
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

        # Retrieve S125 from Laputop
        laputop = frame[reco]
        laputop_params = frame[reco+'Params']
        params = I3LaputopParams.from_frame(frame, reco+'Params')
        log_s125 = params.value(Par.Log10_S125)

        for i, key in enumerate(feats):
            if key == 's125':
                feature = log_s125
            elif key == 'laputop_zen':
                feature = np.sin(laputop.dir.zenith - np.pi/2.)
            elif key == 'charges':
                feature = charges
            elif key == 'laputop_ic':
                feature = frame[reco+'_inice_FractionContainment'].value
            elif key == 'llh_ratio':
                feature = frame[reco+'_IceTopLLHRatio']['LLH_Ratio']

            if i == 0:
                features = feature
            else:
                features = np.column_stack((features,feature))

        for index in ['2_0','2_7','3_0']:
            score = random_forests['alpha_'+index].predict_proba(features).T[1][0]
            frame[reco+'_alpha_'+index+'_score'] = dataclasses.I3Double(score)

def cut_events(frame, recos=[]):
    for reco in recos:
        for index in ['2_0','2_7','3_0']:
            if frame[reco+'_alpha_'+index+'_score'] > 0.7:
                return True

    return False

def main(args, inputFiles):
    
    gcdfile = [args.gcdfile]

    tray = I3Tray()
    tray.AddModule('I3Reader', 'Reader', FilenameList=gcdfile + inputFiles)

    tray.AddSegment(uncompress, 'uncompress')

    #---------------------------------------------------------------------
    # Cut Small Stations

    tray.AddModule(count_icetop_stations,'count_icetop_stations')
    tray.AddModule(cut_small,'cut_small')

    #---------------------------------------------------------------------
    # Clean IceCube pulses

    tray.AddSegment(icecube_cleaning, 'icecube_cleaning')

    #---------------------------------------------------------------------
    # Add systematic reconstructions

    tray.AddSegment(run_laputop, 'laputop_lambda_up',
                    lambda_val=lambdas[args.year]+0.2,
                    laputop_name='LaputopLambdaUp')
    tray.AddSegment(run_laputop, 'laputop_lambda_down',
                    lambda_val=lambdas[args.year]-0.2,
                    laputop_name='LaputopLambdaDown')
    tray.AddModule(shift_s125, 'shift_s125')

    #---------------------------------------------------------------------
    # Calculate IceTop LLHRatio
    pf = '/data/user/hpandya/gamma_combined_scripts/resources/'
    pickles = {'IC86.2011':pf+'12622_2011GammaSim_BurnSample_2011.pickle',
               'IC86.2012':pf+'12533_2012GammaSim_BurnSample_2012.pickle',
               'IC86.2013':pf+'12612_2013GammaSim_BurnSample_2013.pickle',
               'IC86.2014':pf+'12613_2014GammaSim_BurnSample_2014.pickle',
               'IC86.2015':pf+'12614_2015GammaSim_BurnSample_2015.pickle'}
    rf = dict()
    rf['alpha_2_0'] = joblib.load('/data/user/zgriffith/rf_models/'+args.year+'/final/forest_2.0.pkl')
    rf['alpha_2_7'] = joblib.load('/data/user/zgriffith/rf_models/'+args.year+'/final/forest_2.7.pkl')
    rf['alpha_3_0'] = joblib.load('/data/user/zgriffith/rf_models/'+args.year+'/final/forest_3.0.pkl')

    recos = ['Laputop', 'LaputopLambdaUp', 'LaputopLambdaDown',
             'LaputopS125Up', 'LaputopS125Down']
    for reco in recos:
        tray.AddModule(calculate_containment, 'containment_'+reco, particle=reco)
        tray.AddModule(quality_cuts,'quality_cuts_'+reco, reco=reco)
        tray.AddModule(laputop_energy, 'reco_energy_'+reco, reco=reco)
        tray.AddModule(IceTop_LLH_Ratio, 'IceTop_LLH_ratio_'+reco)(
                       ("Track", reco), 
                       ("Output", reco+'_IceTopLLHRatio'),
                       #("TwoDPDFPickle", pickles['IC86.'+args.year]),
                       ("TwoDPDFPickleYear", args.year),
                       ("GeometryHDF5", '/data/user/zgriffith/llhratio_files/geometry.h5'),
                       ("highEbins", True))
        tray.AddModule(apply_random_forest, 'apply_random_forest_'+reco,
                       random_forests=rf, reco=reco)

    tray.AddModule(cut_events, 'cut_events',
                   recos=recos)
    # Write events to an HDF file
    wanted = select_keys()
    hdf = I3HDFTableService(args.output)
    tray.AddModule(I3TableWriter, tableservice=hdf,
                   keys=wanted, SubEventStreams=['ice_top'])

    tray.AddModule('TrashCan', 'Done')
    tray.Execute()
    tray.Finish()

if __name__ == "__main__":
    import sys, os.path
    from optparse import OptionParser

    parser = OptionParser(usage='%s [args] -o <filename>.i3[.bz2|.gz] {i3 file list}'%os.path.basename(sys.argv[0]))
    parser.add_option("-o", "--output", action="store", type="string",
                      help="Output file name", metavar="BASENAME")
    parser.add_option("--year", help="dataset year")
    parser.add_option('-g', '--gcdfile',
                      default='/Users/javierg/IceCubeData/GeoCalibDetectorStatus_IC79.55380_L2a.i3',
                      help='Manually specify the GCD file to be used.  For data, you should generate a GCD first.')

    (args, inputFiles) = parser.parse_args()

    #Check everything is okay and run
    ok = True
    if not os.path.exists(args.gcdfile):
        print " - GCD file %s not found!"%args.gcdfile
        ok = False

    if not args.output:
        print " - Output file not specified!"
        ok = False

    if not ok:
        print ''
        parser.print_help()

    if ok and len(inputFiles) > 0:
        main(args, inputFiles)
