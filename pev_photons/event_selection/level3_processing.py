#!/usr/bin/env python

########################################################################
# Process Level3 Data files 
########################################################################

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

from llh_ratio_i3_module import IceTop_LLH_Ratio

from level3_booking_keys import select_keys
from icecube_cleaning import icecube_cleaning

def quality_cuts(frame):
    """ Apply quality cuts to the data. """

    keep = True
    cuts = frame['IT73AnalysisIceTopQualityCuts']
    for key in cuts.keys():
        if key != 'Laputop_FractionContainment':
            keep = keep&cuts[key]
    keep = keep & (frame['Laputop_FractionContainment'] < 1.0)
    laputop = frame['Laputop']
    laputop_params = frame['LaputopParams']
    keep = keep & (laputop.dir.zenith < np.arccos(0.8))

    Par = LaputopParameter
    params = I3LaputopParams.from_frame(frame, 'LaputopParams')
    s125 = 10 ** params.value(Par.Log10_S125)
    keep = keep & (s125 > 10**-0.25)
    return keep

def calculate_containments(frame):
    """ Calculate geometry containment values using Kath's method. """

    scaling = phys_services.I3ScaleCalculator(frame['I3Geometry'])

    if 'MCPrimary' in frame:
        frame.Put('MCPrimary_FractionContainment',
                  dataclasses.I3Double(scaling.scale_icetop(frame['MCPrimary'])))
        frame.Put('MCPrimary_inice_FractionContainment',
                  dataclasses.I3Double(scaling.scale_inice(frame['MCPrimary'])))

    if 'Laputop' in frame:
        frame.Put('Laputop_inice_FractionContainment',
                  dataclasses.I3Double(scaling.scale_inice(frame['Laputop'])))

    return

def count_icetop_stations(frame):
    """ Count the number of stations hit in IceTop """

    if 'IceTopHLCSeedRTPulses' in frame:
        nstation = count_stations(dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'IceTopHLCSeedRTPulses')) 
        frame.Put('NStation', icetray.I3Int(nstation))

    return 

def laputop_energy(frame):
    """ Calculate Laputop Energy From S125 """

    Par = LaputopParameter
    params = I3LaputopParams.from_frame(frame, 'LaputopParams')
    s125 = 10 ** params.value(Par.Log10_S125)

    coszen=np.cos(frame['Laputop'].dir.zenith)

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

    frame.Put("Laputop_E" , dataclasses.I3Double(10**mixed_energy))

    return

def cut_small(frame):
    """ Ensure small events are removed. """

    if frame['NStation'] < 5:
        return False
    elif not frame.Has('IceTopLaputopSeededSelectedSLC'):
        return False
    return 

def apply_random_forest(frame, random_forests, isMC):
    """ Produces the Random Forest score for each event, then cuts events with
        a score <0.2 in either classifier.  This is necessary to limit final
        file size for storing the events. """

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
    laputop = frame['Laputop']
    laputop_params = frame['LaputopParams']
    Par = LaputopParameter
    params = I3LaputopParams.from_frame(frame, 'LaputopParams')
    log_s125 = params.value(Par.Log10_S125)

    for i, key in enumerate(feats):
        if key == 's125':
            feature = log_s125
        elif key == 'laputop_zen':
            feature = np.sin(laputop.dir.zenith - np.pi/2.)
        elif key == 'charges':
            feature = charges
        elif key == 'laputop_ic':
            feature = frame['Laputop_inice_FractionContainment'].value
        elif key == 'llh_ratio':
            feature = frame['IceTopLLHRatio']['LLH_Ratio']

        if i == 0:
            features = feature
        else:
            features = np.column_stack((features,feature))

    # Keep all events if MC.  For data, limit to candidate events.
    keep = isMC

    for index in ['2_0','2_7','3_0']:
        score = random_forests['alpha_'+index].predict_proba(features).T[1][0]
        frame['alpha_'+index+'_score'] = dataclasses.I3Double(score)

        # Keep data events which pass any of the threshold criteria.
        if score > 0.7:
            keep = True

    return keep

def main(options, inputFiles):
    
    gcdfile = [options.gcdfile]

    tray = I3Tray()
    tray.AddModule('I3Reader', 'Reader', FilenameList=gcdfile + inputFiles)

    tray.AddSegment(uncompress, 'uncompress')

    tray.AddModule(quality_cuts, 'quality_cuts')

    tray.AddModule(calculate_containments,'calculate_containments')
    tray.AddModule(count_icetop_stations,'count_icetop_stations')
    tray.AddModule(cut_small,'cut_small')
    tray.AddModule(laputop_energy,'laputop_energy')

    # Calculate IceTop LLHRatio
    pf = '/data/user/hpandya/gamma_combined_scripts/resources/'
    pickles = {'IC86.2011':pf+'12622_2011GammaSim_BurnSample_2011.pickle',
               'IC86.2012':pf+'12533_2012GammaSim_BurnSample_2012.pickle',
               'IC86.2013':pf+'12612_2013GammaSim_BurnSample_2013.pickle',
               'IC86.2014':pf+'12613_2014GammaSim_BurnSample_2014.pickle',
               'IC86.2015':pf+'12614_2015GammaSim_BurnSample_2015.pickle'}
    tray.AddModule(IceTop_LLH_Ratio, 'IceTop_LLH_ratio')(
                   ("TwoDPDFPickle", pickles['IC86.'+options.year]),
                   ("GeometryHDF5", '/data/user/zgriffith/llhratio_files/geometry.h5'),
                   ("highEbins", True))

    # Clean IceCube pulses
    tray.AddSegment(icecube_cleaning, 'icecube_cleaning')

    # Calculate Random Forest score
    rf = dict()
    rf['alpha_2_0'] = joblib.load('/data/user/zgriffith/rf_models/'+options.year+'/final/forest_2.0.pkl')
    rf['alpha_2_7'] = joblib.load('/data/user/zgriffith/rf_models/'+options.year+'/final/forest_2.7.pkl')
    rf['alpha_3_0'] = joblib.load('/data/user/zgriffith/rf_models/'+options.year+'/final/forest_3.0.pkl')
    isMC = 'sim' in options.output
    tray.AddModule(apply_random_forest, 'apply_random_forest',
                   random_forests=rf, isMC=isMC)

    # Write events to an HDF file
    wanted = select_keys()
    hdf = I3HDFTableService(options.output)
    tray.AddModule(I3TableWriter, tableservice=hdf,
                   keys=wanted, SubEventStreams=['ice_top'])

    tray.AddModule('TrashCan', 'Done')
    tray.Execute()
    tray.Finish()

if __name__ == "__main__":
    import sys, os.path
    from optparse import OptionParser

    parser = OptionParser(usage='%s [options] -o <filename>.i3[.bz2|.gz] {i3 file list}'%os.path.basename(sys.argv[0]))
    parser.add_option("-o", "--output", action="store", type="string",
                      help="Output file name", metavar="BASENAME")
    parser.add_option("--year", help="dataset year")
    parser.add_option('-g', '--gcdfile',
                      default='/Users/javierg/IceCubeData/GeoCalibDetectorStatus_IC79.55380_L2a.i3',
                      help='Manually specify the GCD file to be used.  For data, you should generate a GCD first.')

    (options, inputFiles) = parser.parse_args()

    #Check everything is okay and run
    ok = True
    if not os.path.exists(options.gcdfile):
        print " - GCD file %s not found!"%options.gcdfile
        ok = False

    if not options.output:
        print " - Output file not specified!"
        ok = False

    if not ok:
        print ''
        parser.print_help()

    if ok and len(inputFiles) > 0:
        main(options, inputFiles)
