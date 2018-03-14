#!/usr/bin/env python

########################################################################
# Process Level3 Data files 
########################################################################

import numpy as np

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

lambdas = {'2011': 2.1, '2012': 2.25, '2013': 2.25,
           '2014': 2.3, '2015': 2.3}
def select_keys(isMC=True):
    it_keys=['I3EventHeader', 'IT73AnalysisIceTopQualityCuts',
             'IceTopMaxSignal', 'StationDensity',
             'IceTopNeighbourMaxSignal', 'IceTopLLHRatio']

    lap_keys = ['', 'Params', '_FractionContainment',
                '_inice_FractionContainment', '_E',
                '_opening_angle', '_quality_cuts']
    for reco in ['', 'Migrad', 'LambdaUp', 'LambdaDown']:
        it_keys += ['Laputop'+reco+key for key in lap_keys]

    MC_keys=['MCPrimary', 'MCPrimaryInfo',
             'MCPrimary_inice_FractionContainment',
             'MCPrimary_FractionContainment']

    analysis_keys = ['hlc_count_TWC','slc_count_TWC','nchannel_TWC',
                     'hlc_charge_TWC', 'slc_charge_TWC', 'mjd_time'
                     'alpha_2_0_score', 'alpha_2_7_score', 'alpha_3_0_score',
                     'NStation', 'quality_cut', 'IceTopLLhRatio']
    for pulsename in ['SRTCoincPulses', 'InIcePulses', 'CoincPulses']:
        analysis_keys += ['all_hlcs_'+pulsename, 'all_slcs_'+pulsename,
                          'all_hlc_charge_'+pulsename, 'all_slc_charge_'+pulsename,
                          'nchannel_'+pulsename]

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

    Par = LaputopParameter
    params = I3LaputopParams.from_frame(frame, reco+'Params')
    s125 = 10 ** params.value(Par.Log10_S125)
    quality_cuts['s125_cut'] = s125 > 10**-0.25
    quality_cuts['beta_cut'] = (params.value(Par.Beta) > 1.4) & (params.value(Par.Beta) < 9.5)

    if isMC:
        frame.Put(reco+'_quality_cuts', quality_cuts)
        return
    else:
        return np.all(quality_cuts.values())

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

def opening_angle(frame, reco='Laputop'):
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
    return

def laputop_energy(frame, reco='Laputop'):

    Par = LaputopParameter
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

def main(args, inputFiles):
    
    tray = I3Tray()
    tray.AddModule('I3Reader', 'Reader',
                   FilenameList=[args.gcdfile] + inputFiles)
    tray.AddSegment(uncompress, 'uncompress')

    recos = ['Laputop']
    if args.run_migrad:
        tray.AddSegment(run_laputop, 'laputop_migrad', algorithm='MIGRAD',
                        laputop_name='LaputopMigrad')
        recos.append('LaputopMigrad')
    if args.run_lambdas:
        tray.AddSegment(run_laputop, 'laputop_lambda_up',
                        lambda_val=lambdas[args.year]+0.2,
                        laputop_name='LaputopLambdaUp')
        recos.append('LaputopLambdaUp')
        tray.AddSegment(run_laputop, 'laputop_lambda_down',
                        lambda_val=lambdas[args.year]-0.2,
                        laputop_name='LaputopLambdaDown')
        recos.append('LaputopLambdaDown')

    for reco in recos:
        tray.AddModule(calculate_containment, 'containment_'+reco, particle=reco)
        tray.AddModule(quality_cuts,'quality_cuts_'+reco, reco=reco,
                       isMC=args.isMC)
        tray.AddModule(laputop_energy, 'reco_energy_'+reco, reco=reco)
        if args.isMC:
            tray.AddModule(opening_angle, 'opening_angle_'+reco, reco=reco)

    if args.isMC:
        tray.AddModule(calculate_containment, 'True_containment',
                       particle='MCPrimary')

    '''
    tray.AddModule(IceTop_LLH_Ratio, 'IceTop_LLH_ratio')(
                   ("TwoDPDFPickleYear", args.year),
                   ("GeometryHDF5", '/data/user/zgriffith/llhratio_files/geometry.h5'),
                   ("highEbins", True))

    tray.AddSegment(icecube_cleaning, 'icecube_cleaning')
    '''

    # Write events to an HDF file
    wanted = select_keys(args.isMC)
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
    parser.add_option('--isMC', action='store_true', default=False,
                   help='MC dataset?')
    parser.add_option('--run_migrad', action='store_true', default=False,
                   help='Run Laputop with MIGRAD?')
    parser.add_option('--run_lambdas', action='store_true', default=False,
                   help='Run Laputop with up and down lambdas?')
    parser.add_option('-g', '--gcdfile',
                      default='/Users/javierg/IceCubeData/GeoCalibDetectorStatus_IC79.55380_L2a.i3',
                      help='Manually specify the GCD file to be used.  For data, you should generate a GCD first.')

    (args, inputFiles) = parser.parse_args()

    #Check everything is okay and run
    ok = True
    if not os.path.exists(args.gcdfile):
        print " - GCD file %s not found!" % args.gcdfile
        ok = False

    if not args.output:
        print " - Output file not specified!"
        ok = False

    if not ok:
        print ''
        parser.print_help()

    if ok and len(inputFiles) > 0:
        main(args, inputFiles)
