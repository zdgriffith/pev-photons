#!/usr/bin/env python

########################################################################
# Level3 processing of IceTop data.
# https://wiki.icecube.wisc.edu/index.php/IceTop_Level3_file_structure
########################################################################

import sys
import os.path
import argparse
import re
import glob

from icecube import icetray
from pev_photons.utils.support import prefix

def get_run_from_filename(input_file):
    result = None
    m = re.search('Run([0-9]+)', input_file)
    if not m:
        raise ValueError('cannot parse %s for Run number' % input_file)
    return int(m.group(1))

def main(args, outputLevel=2):
    from I3Tray import I3Tray
    from icecube import dataio, icetop_Level3_scripts, dataclasses, phys_services, frame_object_diff
    from icecube.icetop_Level3_scripts import icetop_globals

    icetray.I3Logger.global_logger.set_level(icetray.I3LogLevel.LOG_ERROR)
    icetray.I3Logger.global_logger.set_level_for_unit('MakeQualityCuts',icetray.I3LogLevel.LOG_INFO)
    
    if not args.L3_gcdfile:
        pre = '/data/ana/CosmicRay/IceTop_level3/'
        if args.isMC:
            gcdfile = [pre+'sim/%s/GCD/Level3_%i_GCD.i3.gz' % (args.detector, args.dataset)]
        else:
            gcdfile = glob.glob(pre+'exp/%s/GCD/Level3_%s_data_Run00%i_????_GCD.i3.gz' % (args.detector, args.detector, args.run))
    else:
        gcdfile = [args.L3_gcdfile]
        
    # Instantiate a tray
    tray = I3Tray()
    tray.AddModule('I3Reader', 'Reader', FilenameList=gcdfile + args.input_files)

    from icecube.frame_object_diff.segments import uncompress
    
    # If the L2 gcd file is not specified, use the base_filename which is used for compressing. Check First whether it exists.
    # If the L2 gcd file is provided (probably in the case when running on your own cluster and when you copied the diff and L2 GCDs there), 
    # then you use this, but you check first whether the filename makes sense (is the same as the base_filename used for compression). 
    def CheckL2GCD(frame):
        geodiff=frame['I3GeometryDiff']
        if args.L2_gcdfile:
            L2_GCD = args.L2_gcdfile
            if os.path.basename(L2_GCD) != os.path.basename(geodiff.base_filename):
                icetray.logging.log_fatal('The provided L2 GCD seems not suited to use for uncompressing the L3 GCD. It needs to have the same filename as the L2 GCD used to create the diff.')
        else:
            L2_GCD = geodiff.base_filename
        if not os.path.exists(L2_GCD):
            icetray.logging.log_fatal('L2 GCD file %s not found' % L2_GCD)

    tray.AddModule(CheckL2GCD,'CheckL2CD',
                   Streams=[icetray.I3Frame.Geometry])

    tray.Add(uncompress,
             base_filename=args.L2_gcdfile) # works correctly if L2_gcdfile is None
        
    tray.AddSegment(icetop_Level3_scripts.segments.level3_IceTop, 'level3_IceTop',
                    detector=args.detector,
                    do_select=args.select,
                    isMC=args.isMC,
                    add_jitter=args.add_jitter,
                    snowLambda=snow_lambda
                    )
    
    if args.do_inice:
        tray.AddSegment(icetop_Level3_scripts.segments.level3_Coinc, 'level3_Coinc',
                        Detector=args.detector,
                        isMC=args.isMC,
                        do_select=args.select,
                        IceTopTrack='Laputop',
                        IceTopPulses='IceTopHLCSeedRTPulses',
                        )

    if args.waveforms:
        from icecube.icetop_Level3_scripts.functions import count_stations
        tray.AddModule(icetop_Level3_scripts.modules.FilterWaveforms, 'FilterWaveforms',   #Puts IceTopWaveformWeight in the frame.
                       pulses=icetop_globals.icetop_hlc_pulses,
                       If = lambda frame: icetop_globals.icetop_hlc_pulses in frame and count_stations(dataclasses.I3RecoPulseSeriesMap.from_frame(frame, icetop_globals.icetop_hlc_pulses)) >= 5)
        tray.AddSegment(icetop_Level3_scripts.segments.ExtractWaveforms, 'IceTop',
                       If= lambda frame: 'IceTopWaveformWeight' in frame and frame['IceTopWaveformWeight'].value!=0)    
                  
    ## Which keys to keep:
    wanted_general=['I3EventHeader',
                    icetop_globals.filtermask,
                    'I3TriggerHierarchy']

    if args.isMC:
        wanted_general+=['MCPrimary',
                         'MCPrimaryInfo',
                         'AirShowerComponents',
                         'IceTopComponentPulses_Electron',
                         'IceTopComponentPulses_ElectronFromChargedMesons',
                         'IceTopComponentPulses_Gamma',
                         'IceTopComponentPulses_GammaFromChargedMesons',
                         'IceTopComponentPulses_Muon',
                         'IceTopComponentPulses_Hadron',
                         ]

    wanted_icetop_filter=['IceTop_EventPrescale',
                          'IceTop_StandardFilter',
                          'IceTop_InFillFilter']
 
    wanted_icetop_pulses=[icetop_globals.icetop_hlc_pulses,
                          icetop_globals.icetop_slc_pulses,
                          icetop_globals.icetop_clean_hlc_pulses,
                          icetop_globals.icetop_tank_pulse_merger_excluded_tanks,
                          icetop_globals.icetop_cluster_cleaning_excluded_tanks,
                          icetop_globals.icetop_HLCseed_clean_hlc_pulses,
                          icetop_globals.icetop_HLCseed_excluded_tanks,
                          icetop_globals.icetop_HLCseed_clean_hlc_pulses+'_SnowCorrected',
                          'TankPulseMergerExcludedSLCTanks',
                          'IceTopLaputopSeededSelectedHLC',  
                          'IceTopLaputopSeededSelectedSLC',                                                                                                                                               
                          'IceTopLaputopSmallSeededSelectedHLC',  
                          'IceTopLaputopSmallSeededSelectedSLC',                                                                                                                                         
                          ]

    wanted_icetop_waveforms=['IceTopVEMCalibratedWaveforms',
                             'IceTopWaveformWeight']

    wanted_icetop_reco=['ShowerCOG',
                        'ShowerPlane',
                        'ShowerPlaneParams',
                        'Laputop',
                        'LaputopParams',
                        'LaputopSnowDiagnostics',
                        'LaputopSmall',
                        'LaputopSmallParams',
                        'IsSmallShower'
                        ]
    
    wanted_icetop_cuts=['Laputop_FractionContainment',
                        'Laputop_OnionContainment',
                        'Laputop_NearestStationIsInfill',
                        'StationDensity',
                        'IceTopMaxSignal',
                        'IceTopMaxSignalInEdge',
                        'IceTopMaxSignalTank',
                        'IceTopMaxSignalString',
                        'IceTopNeighbourMaxSignal',
                        'IT73AnalysisIceTopQualityCuts',
                        ]

    wanted=wanted_general+wanted_icetop_filter+wanted_icetop_pulses+wanted_icetop_waveforms+wanted_icetop_reco+wanted_icetop_cuts
    
    
    if args.do_inice:
        wanted_inice_pulses=[icetop_globals.inice_pulses,
                             icetop_globals.inice_coinc_pulses,
                             icetop_globals.inice_clean_coinc_pulses,
                             icetop_globals.inice_clean_coinc_pulses+'TimeRange',
                             icetop_globals.inice_clean_coinc_pulses+'_Balloon',
                             'InIceDSTPulses',
                             'I3SuperDST',
                             'SaturationWindows',
                             'CalibrationErrata',
                             'SRT'+icetop_globals.inice_coinc_pulses,
                             'NCh_'+icetop_globals.inice_clean_coinc_pulses]

        wanted_inice_reco=['Millipede',
                           'MillipedeFitParams',
                           'Millipede_dEdX',
                           'Stoch_Reco',
                           'Stoch_Reco2',
                           'I3MuonEnergyLaputopCascadeParams',
                           'I3MuonEnergyLaputopParams'
                           ]
   
        wanted_inice_cuts=['IT73AnalysisInIceQualityCuts']

        wanted_inice_muon=['CoincMuonReco_LineFit',
                           'CoincMuonReco_SPEFit2',
                           'CoincMuonReco_LineFitParams',
                           'CoincMuonReco_SPEFit2FitParams',
                           'CoincMuonReco_MPEFit',
                           'CoincMuonReco_MPEFitFitParams',
                           'CoincMuonReco_MPEFitMuEX',
                           'CoincMuonReco_CVMultiplicity',
                           'CoincMuonReco_CVStatistics',
                           'CoincMuonReco_MPEFitCharacteristics',
                           'CoincMuonReco_SPEFit2Characteristics',
                           'CoincMuonReco_MPEFitTruncated_BINS_Muon',
                           'CoincMuonReco_MPEFitTruncated_AllBINS_Muon',
                           'CoincMuonReco_MPEFitTruncated_ORIG_Muon',
                           'CoincMuonReco_SPEFit2_D4R_CascadeParams',
                           'CoincMuonReco_SPEFit2_D4R_Params',
                           'CoincMuonReco_MPEFitDirectHitsC'
                           ]

        wanted = wanted + wanted_inice_pulses + wanted_inice_reco + wanted_inice_cuts + wanted_inice_muon

    tray.AddModule('Keep', 'DropObjects',
                   Keys=wanted
                   )
    
    if output.replace('.bz2', '').replace('.gz','')[-3:] == '.i3':
        tray.AddModule('I3Writer', 'i3-writer',
                       Filename=output,
                       DropOrphanStreams=[icetray.I3Frame.DAQ],
                       streams=[icetray.I3Frame.DAQ, icetray.I3Frame.Physics],
                       )
    else:
        raise Exception('I do not know how to handle files with extension %s' % output.replace('.bz2', '').replace('.gz','')[-3:])

    if args.livetime or args.histos:
        from icecube.production_histograms import ProductionHistogramModule
        
        if args.histos:
            tray.AddSegment(icetop_Level3_scripts.segments.MakeHistograms, 'makeHistos', OutputFilename=args.histos, isMC=args.isMC)

        if not args.isMC and args.livetime:
            tray.Add(ProductionHistogramModule, 'LivetimeHistogram',
                     Histograms = [icetop_Level3_scripts.histograms.Livetime],
                     OutputFilename = args.livetime
                     )

    tray.AddModule( 'TrashCan' , 'Done' )
    
    # Execute the Tray
    if args.n is None:
        tray.Execute()
    else:
        tray.Execute(args.n)

    tray.Finish()
    

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--input_files', help='Input file(s)', nargs='*')
    p.add_argument('-n', type=int, help='Number of frames to process.')
    p.add_argument('--detector',
                   help='Detector configuration name, eg: IC79, IC86.2011.')
    p.add_argument('--waveforms', action='store_true',
                   help='Extract waveforms (only if more than 5 stations in HLC VEM pulses)')
    p.add_argument('--select', action='store_true', default=False,
                   help=('Apply selection (containment, max. signal and min. stations).'
                         'Default is to calculate variables but not filter'))
    p.add_argument('--L2_gcdfile', help='The L2 GCD file to be used.')
    p.add_argument('--L3_gcdfile', help='The L3 (diff) GCD file to be used.')
    p.add_argument('--isMC', action='store_true', help= 'Is this data or MC?')
    p.add_argument('--dataset', type=int, help= 'Dataset number for MC.')
    p.add_argument('--run', type=int, help= 'Run number, needed for data.')
    p.add_argument('--add_jitter', action='store_true',
                   help='Do we add extra jitter on the IT pulses?')
    p.add_argument('--do_inice', action='store_true',
                   help= 'Also do in-ice reco?')
    p.add_argument('--histos', help='Histograms file name. Needs to be a pickle file.')
    p.add_argument('--livetime', action='store',
                   help='Livetime file name, only needed for data. Needs to be a pickle file.')
    args = p.parse_args()
    
    icetray.I3Logger.global_logger.set_level(icetray.I3LogLevel.LOG_INFO)

    outDir = prefix+'datasets/level3/%s/' % args.dataset
    start = re.split('\.', args.input_files[0])[-3][-6:]
    end = re.split('\.', args.input_files[-1])[-3][-6:]
    output = '%s/%s_part%s-%s.i3.gz' % (outDir, args.dataset, start, end)

    SnowFactor = {'IC79': 2.1, 'IC86.2011':2.25,
                  'IC86.2012':2.25, 'IC86.2013':2.3,
                  'IC86.2014':2.3, 'IC86.2015':2.3}
    snow_lambda = SnowFactor[args.detector]

    if not args.isMC:  # Filename is only really needed for data...
        if args.run is None:
            args.run = get_run_from_filename(args.input_files[0])
            icetray.logging.log_info('Auto-detected run %i' % args.run)

    main(args, output=output, snow_lambda=snow_lambda)
