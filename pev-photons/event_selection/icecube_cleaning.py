import math
import numpy as np
from icecube import icetray, dataio, dataclasses, phys_services, toprec, millipede 
from I3Tray import *
from icecube import coinc_twc

def rounder(a, MinClip):
    return math.ceil(float(a) / MinClip) * MinClip

def clean_pulses(frame,pulsename='InIcePulses',reco='Laputop', pulses_to_keep='None'):
    if pulsename not in frame:
        return

    geo       = frame['I3Geometry']
    laputop   = frame[reco]
    allpulses = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, pulsename)
    triggers  = dataclasses.I3TriggerHierarchy.from_frame(frame, 'I3TriggerHierarchy')

    # Use this method to select "best" IT trigger and set time off of that
    it_pulses = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, 'CleanedHLCTankPulses')
    p_times   = []
    for (omkey, pulses) in it_pulses:
        for p in pulses:
            p_times.append(p.time)

    t_min        = min(p_times) 
    it_times     = np.array([trigger.time for trigger in triggers if trigger.key.source == dataclasses.ICE_TOP])
    trigger_time = min(it_times, key=lambda x:abs(x-t_min))
    length = len(allpulses)
    is_hlc = np.zeros(length) 

    #Per Pulse Info
    keep_pulses = pulses_to_keep != 'None' 

    if keep_pulses:
        isMC   = frame.Has('MCPrimary')
        pulse_doms  = np.zeros(length) 
        pulse_times = np.zeros(length) 
        pulse_dists = np.zeros(length) 
        pulse_coinc = np.zeros(length) 
        pulse_SRT   = np.zeros(length) 

        if isMC:
            primary          = frame['MCPrimary']
            true_pulse_dists = np.zeros(length) 

    hlcs       = 0
    slcs       = 0
    nchannel   = 0
    hlc_charge = 0
    slc_charge = 0

    for i, (omkey, pulses) in enumerate(allpulses):
        omgeo   = geo.omgeo[omkey]
        d_pulse = phys_services.I3Calculator.closest_approach_distance(laputop, omgeo.position)

        if keep_pulses:
            if frame.Has('MCPrimary'):
                true_d  = phys_services.I3Calculator.closest_approach_distance(primary, omgeo.position)

        dom = 0
        for j, p in enumerate(pulses):

            #Timing Information
            t_diff  = p.time - trigger_time 
            cosZen  = rounder(np.cos(laputop.dir.zenith),0.05)
            t_dom   = 0.05*(omkey[1]-1)*1000
            t_start = (4800 + t_dom)/cosZen
            t_end   = (4800+1800+t_dom)/cosZen

            #Time Window Cleaning
            if t_diff > 3500 and t_diff < 11500:
                is_hlc[i] += p.flags & dataclasses.I3RecoPulse.PulseFlags.LC

                if is_hlc[i]:
                    if dom == 0:
                        nchannel += 1
                        dom      += 1
                    hlcs += 1 
                    hlc_charge += p.charge
                else:
                    if omkey[1] < 17 and np.abs(d_pulse) < 130:
                        if t_diff > t_start and t_diff < t_end:
                            slcs += 1
                            slc_charge += p.charge
                            if dom == 0:
                                nchannel += 1
                                dom      += 1

                if keep_pulses:
                    pulse_doms[i]  += omkey[1]
                    pulse_dists[i] += d_pulse
                    pulse_times[i] += t_diff
                    if isMC:
                        true_pulse_dists[i] += true_d

    #--------------------- Histogramming Time -------------------#

    #HLCs 
    if keep_pulses:
        mask = np.equal(is_hlc,1) if pulses_to_keep=='hlc' else np.equal(is_hlc,0)
        frame[pulses_to_keep]          = dataclasses.I3MapStringVectorDouble()
        frame[pulses_to_keep]['time']  = pulse_times[mask]
        frame[pulses_to_keep]['dom']   = pulse_doms[mask]
        frame[pulses_to_keep]['dist']  = pulse_dists[mask]
        if isMC:
            frame[pulses_to_keep]['true_dist'] = true_pulse_dists[mask]

    if frame.Has('hlc_count_TWC'):
        frame.Delete('hlc_count_TWC')
        frame.Delete('slc_count_TWC')
    frame['hlc_count_TWC']  = icetray.I3Int(hlcs)
    frame['slc_count_TWC']  = icetray.I3Int(slcs)
    frame['nchannel_TWC']   = icetray.I3Int(nchannel)
    frame['hlc_charge_TWC'] = dataclasses.I3Double(hlc_charge)
    frame['slc_charge_TWC'] = dataclasses.I3Double(slc_charge)
    frame['mjd_time']       = dataclasses.I3Double(frame['I3EventHeader'].start_time.mod_julian_day_double)

    return

def count_pulses(frame, pulsename='SRTCoincPulses'):
    if pulsename not in frame:
        return
        
    hlcs       = 0
    slcs       = 0
    nchannel   = 0
    hlc_charge = 0
    slc_charge = 0
    allpulses  = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, pulsename)

    for i, (omkey, pulses) in enumerate(allpulses):
        dom = 0
        for j, p in enumerate(pulses):
                if dom == 0:
                    nchannel += 1
                    dom      += 1
                if p.flags & dataclasses.I3RecoPulse.PulseFlags.LC:
                    hlcs += 1
                    hlc_charge += p.charge
                else:
                    slcs += 1
                    slc_charge += p.charge

    frame['nchannel_'+pulsename] = icetray.I3Int(nchannel)
    frame['all_hlcs_'+pulsename] = icetray.I3Int(hlcs)
    frame['all_slcs_'+pulsename] = icetray.I3Int(slcs)
    frame['all_hlc_charge_'+pulsename] = dataclasses.I3Double(hlc_charge)
    frame['all_slc_charge_'+pulsename] = dataclasses.I3Double(slc_charge)

    return

def count_icecube_hits(frame, pulse_series='InIcePulses', reco='Laputop'):
    """ Count the number of HLCs and SLCs in IceCube """

    if pulse_series not in frame:
        return

    geo = frame['I3Geometry']
    laputop = frame[reco]
    allpulses = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, pulse_series)

    hlcs = []
    slcs = 0
    for omkey, pulses in allpulses:
        omgeo = geo.omgeo[omkey]
        d_pulse = phys_services.I3Calculator.closest_approach_distance(laputop, omgeo.position)
        hlcs += [(p.flags & dataclasses.I3RecoPulse.PulseFlags.LC) for p in pulses]

        top_list = [1, 2, 3, 4, 5, 6]
        if omkey[1] in top_list:
            for p in pulses:
                if (p.flags & dataclasses.I3RecoPulse.PulseFlags.LC) == 0:
                    if np.abs(d_pulse) < 200 and p.time > 14800 and p.time < 16500:
                        slcs += 1

    frame['hlc_count_'+pulse_series] = icetray.I3Int(hlcs.count(1))
    frame['slc_count_'+pulse_series] = icetray.I3Int(slcs)

    return

def icecube_cleaning(tray, name):
    """ Tray Segment to apply IceCube Cleaning """

    pulse_series = ['InIcePulses', 'SRTCoincPulses', 'CoincPulses']
    for series in pulse_series:
        tray.AddModule(count_icecube_hits, 'count_'+series,
                       pulse_series=series)
    tray.AddModule(count_pulses, 'count_pulses')
    tray.AddModule(clean_pulses, 'clean_pulses')
