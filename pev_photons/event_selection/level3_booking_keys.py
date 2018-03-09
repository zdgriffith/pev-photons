from icecube import icetray, dataclasses, toprec, phys_services, simclasses
from det_to_shower_coord_converter import PulsesInShowerCS

it_keys=["Laputop","LaputopParams","ShowerCOG","ShowerPlane","ShowerPlaneParams",
                  'FilterMask','I3EventHeader',"IT73AnalysisIceTopQualityCuts",
                  dict(key='Laputop',
                        converter = phys_services.converters.I3RecoInfoConverter('IceTopHLCSeedRTPulses'),
                        name = 'Laputop_info'),
                  dict(key ='IceTopHLCSeedRTPulses',
                       converter = dataclasses.converters.I3RecoPulseSeriesMapConverter(bookGeometry=True),                                                                            
                       name = 'IceTopHLCSeedRTPulses'),
                  dict(key ='IceTopHLCSeedRTPulses',
                       converter = phys_services.converters.I3EventInfoConverterFromRecoPulses(),
                       name = 'IceTopHLCSeedRTPulses_info')
                  ]

it_keys.append('Laputop_FractionContainment')
it_keys.append('BetaCutPassed') #don't see it in level3 files i processed today, FIXME . 12 jan 2016
it_keys.append('Laputop_cleanedHLC')
it_keys.append('Laputop_cleanedHLCParams')
it_keys.append('IceTopMaxSignal')
it_keys.append('StationDensity')
it_keys.append('IceTopNeighbourMaxSignal')
it_keys.append('IsSmallShower_cleanedHLC')
it_keys.append('IsSmallShower')
it_keys.append('IceTopLLHRatio')
it_keys.append('NStation_cleanedHLC')
it_keys.append('IceTopLaputopSeededSelectedMCPriHLC')
it_keys.append('IceTopLaputopSeededSelectedMCPriSLC')
it_keys += [dict(key='IceTopLaputopSeededSelectedHLC', converter=PulsesInShowerCS(axis='Laputop'))]
it_keys += [dict(key='IceTopLaputopSeededSelectedSLC', converter=PulsesInShowerCS('Laputop',))]
it_keys += [dict(key='IceTopHLCSeedRTPulses', converter=PulsesInShowerCS(axis='Laputop'),
                    name='IceTopHLCSeedRTPulses_Laputop')]
it_keys += [dict(key ='IceTopLaputopSeededSelectedSLC',
                   converter = phys_services.converters.I3EventInfoConverterFromRecoPulses(),
                   name = 'IceTopLaputopSeededSelectedSLC_info')]
it_keys += [dict(key ='IceTopLaputopSeededSelectedHLC',
                       converter = phys_services.converters.I3EventInfoConverterFromRecoPulses(),
                       name = 'IceTopLaputopSeededSelectedHLC_info'),
                      dict(key ='CleanedHLCTankPulses',
                      converter = dataclasses.converters.I3RecoPulseSeriesMapConverter(bookGeometry=True),
                           name = 'CleanedHLCTankPulses'),
                      dict(key ='CleanedHLCTankPulses',
                           converter = phys_services.converters.I3EventInfoConverterFromRecoPulses(),
                           name = 'CleanedHLCTankPulses_info')
                       ]

MC_keys=["MCPrimary","MCPrimaryInfo"]

ic_keys=[ #dict(key ='CleanedCoincPulses',
                  #converter = dataclasses.converters.I3RecoPulseSeriesMapConverter(bookGeometry=True),
                  #name = 'CleanedCoincPulses'),
             #dict(key ='SRTCoincPulses',
             #     converter = dataclasses.converters.I3RecoPulseSeriesMapConverter(bookGeometry=True),
             #     name = 'SRTCoincPulses'),
             #dict(key ='InIcePulses',
             #     converter = dataclasses.converters.I3RecoPulseSeriesMapConverter(bookGeometry=True),
             #     name = 'InIcePulses'),
             dict(key ='CoincPulses',
                  converter = phys_services.converters.I3EventInfoConverterFromRecoPulses(),
                  name = 'CoincPulses_info'),
             dict(key ='SRTCoincPulses',
                  converter = phys_services.converters.I3EventInfoConverterFromRecoPulses(),
                  name = 'SRTCoincPulses_info'),
             dict(key ='InIcePulses',
                  converter = phys_services.converters.I3EventInfoConverterFromRecoPulses(),
                  name = 'InIcePulses_info')
                  ]

Frame_object_llh = 'GammaRayAnalysis_LLH' 
analysis_keys = ['hlc_count_TWC','slc_count_TWC','nchannel_TWC',
                           'hlc_charge_TWC', 'slc_charge_TWC','mjd_time'
                            'MCPrimary_inice_FractionContainment', 'MCPrimary_FractionContainment',
                            Frame_object_llh,
                            'Laputop_cleanedHLC_FractionContainment','Laputop_cleanedHLC_inice_FractionContainment',
                            'quality_cut',
                            'alpha_2_0_score', 'alpha_2_7_score', 'alpha_3_0_score',
                            'Laputop_E','NStation', 'Laputop_inice_FractionContainment']

for pulsename in ['SRTCoincPulses','InIcePulses','CoincPulses']:
    analysis_keys.append('all_hlcs_'+pulsename)
    analysis_keys.append('all_slcs_'+pulsename)
    analysis_keys.append('all_hlc_charge_'+pulsename)
    analysis_keys.append('all_slc_charge_'+pulsename)
    analysis_keys.append('nchannel_'+pulsename)

it_extra_keys=[]
it_extra_keys.append('IceTopComponentPulses_Gamma')
it_extra_keys.append('IceTopComponentPulses_Electron')
it_extra_keys.append('IceTopComponentPulses_GammaFromChargedMesons')
it_extra_keys.append('IceTopComponentPulses_ElectronFromChargedMesons')
it_extra_keys.append('IceTopComponentPulses_Muon')
it_extra_keys.append('IceTopComponentPulses_Hadron')
it_extra_keys += [dict(key='IceTopHLCSeedRTPulses', converter=PulsesInShowerCS(axis='MCPrimary'),
                    name='IceTopHLCSeedRTPulses_MCPrimary')]

def select_keys(isMC = True, do_inice=True, extra_booking=False):
    book_keys=it_keys+analysis_keys
    if isMC:
        book_keys+=MC_keys
    if do_inice:
        book_keys+=ic_keys
    if extra_booking:
        book_keys+=it_extra_keys

    return book_keys


