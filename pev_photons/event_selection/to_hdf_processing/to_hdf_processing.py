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
from pev_photons.event_selection.level3_booking_keys import select_keys
from pev_photons.event_selection.icecube_cleaning import icecube_cleaning

def quality_cuts(frame, isMC=False):
    """ Apply quality cuts. """

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

    if isMC:
        frame.Put('quality_cut', icetray.I3Bool(bool(keep)))
    else:
        return keep

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

def main(options, inputFiles):
    
    gcdfile = [options.gcdfile]

    tray = I3Tray()
    tray.AddModule('I3Reader', 'Reader', FilenameList=gcdfile + inputFiles)

    tray.AddSegment(uncompress, 'uncompress')

    isMC = True
    tray.AddModule(quality_cuts, 'quality_cuts', isMC=isMC)

    tray.AddModule(calculate_containment, 'Laputop_containment',
                   particle='Laputop')
    if isMC:
        tray.AddModule(calculate_containment, 'True_containment',
                       particle='MCPrimary')

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
