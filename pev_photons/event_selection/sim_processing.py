#!/usr/bin/env python

import numpy as np
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, recclasses, toprec, phys_services
from icecube import coinc_twc, static_twc, SeededRTCleaning
from icecube.icetop_Level3_scripts.functions import count_stations 

from icecube.recclasses import I3LaputopParams, LaputopParameter

from run_laputop import laputop_migrad

def get_keys():
    keys = ['IceTopMaxSignal',
            'IceTopMaxSignalInEdge',
            'IceTopMaxSignalString',
            'IceTopNeighbourMaxSignal',
            'IceTop_StandardFilter',
            'MCPrimary',
            'StationDensity',
            'NStation']

    lap_keys = ['', 'Params', '_FractionContainment', '_E',
                '_opening_angle', '_quality_cuts']
    for reco in ['Laputop', 'LaputopMigrad']:
        keys += [reco+key for key in lap_keys]

    return keys

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

def count_icetop_stations(frame):
    """ Count the number of stations hit in IceTop """

    if 'IceTopHLCSeedRTPulses' in frame:
        nstation = count_stations(dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'IceTopHLCSeedRTPulses')) 
        frame.Put('NStation', icetray.I3Int(nstation))

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

def quality_cuts(frame, reco='Laputop'):
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
    frame.Put(reco+'_quality_cuts', quality_cuts)

    return

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

def main(options, inputFiles):
    
    gcdfile = [options.gcdfile]
    outfile=options.output

    tray = I3Tray()
    tray.AddModule( 'I3Reader', 'Reader', FilenameList = gcdfile + inputFiles)

    from icecube.frame_object_diff.segments import uncompress
    tray.AddSegment(uncompress, "uncompress")

    tray.AddModule(count_icetop_stations,'count_icetop_stations')

    tray.AddSegment(laputop_migrad, 'laputop_migrad')
    for reco in ['Laputop', 'LaputopMigrad']:
        tray.AddModule(calculate_containment, 'containment_'+reco, particle=reco)
        tray.AddModule(laputop_energy, 'reco_energy_'+reco, reco=reco)
        tray.AddModule(opening_angle, 'opening_angle_'+reco, reco=reco)
        tray.AddModule(quality_cuts,'quality_cuts_'+reco, reco=reco)

    #--------------------------------------------

    from icecube.tableio import I3TableWriter
    from icecube.hdfwriter import I3HDFTableService
    hdf = I3HDFTableService(options.output)
    tray.AddModule(I3TableWriter, tableservice=hdf,
                   keys=get_keys(), SubEventStreams=['ice_top'])

    #--------------------------------------------

    tray.AddModule( 'TrashCan' , 'Done' )
    tray.Execute()
    tray.Finish()

if __name__ == "__main__":
    import sys, os.path
    from optparse import OptionParser

    parser = OptionParser(usage='%s [options] -o <filename>.i3[.bz2|.gz] {i3 file list}'%os.path.basename(sys.argv[0]))
    parser.add_option("-o", "--output", action="store", type="string", dest="output", help="Output file name", metavar="BASENAME")
    parser.add_option('-g', '--gcdfile', default='/Users/javierg/IceCubeData/GeoCalibDetectorStatus_IC79.55380_L2a.i3',
                      dest='gcdfile', help='Manually specify the GCD file to be used.   For data, you should generate a GCD first')

    #ShowerLLH Options
    parser.add_option('--gridFile', dest='gridFile',
            help='File containing locations for iterative grid search')
    parser.add_option('--llhFile', dest='llhFile',
            help='File with llh tables for reconstruction')

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
