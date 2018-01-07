#!/usr/bin/env python

import numpy as np
from I3Tray import I3Tray
from icecube import icetray, dataio, dataclasses, recclasses, toprec
from icecube import coinc_twc, static_twc, SeededRTCleaning

from icecube.recclasses import I3LaputopParams, LaputopParameter

def laputop_energy(frame):

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

def quality_cuts(frame):
    keep = True
    cuts = frame['IT73AnalysisIceTopQualityCuts']
    for key in cuts.keys():
        if key != 'Laputop_FractionContainment':
            keep = keep&cuts[key]
    keep = keep&(frame['Laputop_FractionContainment'] <1.0)
    laputop = frame['Laputop']
    laputop_params = frame['LaputopParams']
    keep = keep&(laputop.dir.zenith < np.arccos(0.8))

    Par = LaputopParameter
    params = I3LaputopParams.from_frame(frame, 'LaputopParams')
    s125 = 10 ** params.value(Par.Log10_S125)
    keep = keep&(s125 > 10**-0.25)
    return keep

def main(options, inputFiles):
    
    gcdfile = [options.gcdfile]
    outfile=options.output

    tray = I3Tray()
    tray.AddModule( 'I3Reader', 'Reader', FilenameList = gcdfile + inputFiles)

    from icecube.frame_object_diff.segments import uncompress
    tray.AddSegment(uncompress, "uncompress")

    tray.AddModule(quality_cuts,'quality_cuts')
    tray.AddModule(laputop_energy, 'reco_energy')

    #--------------------------------------------

    from icecube.tableio import I3TableWriter
    from icecube.hdfwriter import I3HDFTableService
    hdf = I3HDFTableService(options.output)
    tray.AddModule(I3TableWriter, tableservice=hdf,
                   keys=['Laputop_E'], SubEventStreams=['ice_top'])

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