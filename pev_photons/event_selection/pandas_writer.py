#!/usr/bin/env python

##############################################
####   Format HDF files for Analysis    ######
##############################################

import numpy as np
import argparse, sys, tables
import time, glob
import pandas as pd

def get_weights(sim, energy, nstations):

    #Function from weighting project
    def norm(emin, emax, eslope):
        if eslope < -1:
            g = eslope+1
            return (emax**g - emin**g)/g
        else:
            return np.log(emax/emin)

    #Integrated Area times Solid Angle
    def int_area(E, theta_max):
        radius = 800*np.greater_equal(E, 10**5) + 300*np.greater_equal(E,10**6) + 300*np.greater_equal(E,10**7)

        return ((radius*100)**2)*(1-np.cos(np.radians(theta_max))**2)*np.pi**2

    
    events = 100*np.array([179, 178, 178, 178, 184, 176, 175, 177, 170, 169, 169, 173, 176,
                           179, 171, 177, 182, 169, 170, 178, 179, 174, 173, 164, 172, 147,
                           147, 125, 111,  92])
    #events = np.load('/data/user/zgriffith/sim_files/'+sim+'_events.npy') 

    # Number of thrown events in an Ebin, normed by the size of the Ebin
    def n_thrown(E):
        indices = np.floor(10*np.log10(E))-50
        if sim == '12622':
            return 60000/norm(10**6,10**6.1,-1)
        else:
            return np.take(events, indices.astype('int'))/norm(10**6,10**6.1,-1)

    #Maximum Zenith Angle
    if sim in ['7006', '7007']:
        max_zen = 40.
    elif sim in ['12360', '12362']:
        max_zen = 65.
    else:
        max_zen = 45.

    weights = int_area(energy,max_zen)*energy/n_thrown(energy)
    if sim == '12622': 
        prescale = 2.*(np.less(nstations, 8)&np.greater(nstations,3))+1.
        return weights/prescale
    else:
        return weights 

def rewrite(file_list, outFile, set_name, isMC):

    dataframe_dict = {}
    t_sim = time.time()
    err   = 0
    err_list = []

    for i, fname in enumerate(file_list):
        print(i)
        f = {}
        try:
            store = pd.HDFStore(fname)
        except:
            print('error, skipping')
            err += 1
            continue
        f['quality_cut']  = store.select('quality_cut').value
        f['standard_filter_cut']  = store.select('IT73AnalysisIceTopQualityCuts').IceTop_StandardFilter
        f['Q_cut']            = store.select('IT73AnalysisIceTopQualityCuts').IceTopMaxSignalAbove6
        f['beta_cut']         = store.select('IT73AnalysisIceTopQualityCuts').BetaCutPassed
        f['loudest_cut']      = store.select('IT73AnalysisIceTopQualityCuts').IceTopMaxSignalInside
        f['neighbor_cut']     = store.select('IT73AnalysisIceTopQualityCuts').IceTopNeighbourMaxSignalAbove4
        f['laputop_cut']      = store.select('IT73AnalysisIceTopQualityCuts').IceTop_reco_succeeded
        f['density_cut']      = store.select('IT73AnalysisIceTopQualityCuts').StationDensity_passed

        f['Nstations']        = store.select('NStation').value
        f['StationDensity']   = store.select('StationDensity').value
        f['mjd_time']         = store.select('I3EventHeader').time_start_mjd
        f['Q_max']            = store.select('IceTopMaxSignal').value
        f['chi2_ndf_ldf']     = store.select('LaputopParams').chi2
        f['chi2_ndf_time']    = store.select('LaputopParams').chi2_time

        #---- Laputop ----#
        f['laputop_azi']      = store.select('Laputop').azimuth
        f['laputop_zen']      = store.select('Laputop').zenith
        f['laputop_x']        = store.select('Laputop').x
        f['laputop_y']        = store.select('Laputop').y
        f['laputop_it']       = store.select('Laputop_FractionContainment').value
        f['laputop_ic']       = store.select('Laputop_inice_FractionContainment').value
        f['s125']             = store.select('LaputopParams').s125
        f['laputop_E']        = store.select('Laputop_E').value

        #---- Separation ----#
        #---- IceTop ----#
        f['llh_ratio']        = store.select('IceTopLLHRatio').LLH_Ratio
        f['llh_ratio_q_r']    = store.select('IceTopLLHRatio').LLH_Gamma_q_r/store.select('IceTopLLHRatio').LLH_Hadron_q_r
        f['llh_ratio_q_t']    = store.select('IceTopLLHRatio').LLH_Gamma_q_t/store.select('IceTopLLHRatio').LLH_Hadron_q_t
        f['llh_ratio_t_r']    = store.select('IceTopLLHRatio').LLH_Gamma_t_r/store.select('IceTopLLHRatio').LLH_Hadron_t_r

        #---- IceCube ----#
        f['twc_hlc_count']     = store.select('hlc_count_TWC').value
        f['twc_slc_count']     = store.select('slc_count_TWC').value
        f['twc_nchannel']      = store.select('nchannel_TWC').value
        f['twc_hlc_charge']    = store.select('hlc_charge_TWC').value
        f['twc_slc_charge']    = store.select('slc_charge_TWC').value

        try:
            f['srt_hlc_count']  = store.select('all_hlcs_SRTCoincPulses').value
            f['srt_slc_count']  = store.select('all_slcs_SRTCoincPulses').value
            f['srt_nchannel']   = store.select('nchannel_SRTCoincPulses').value
            f['srt_hlc_charge'] = store.select('all_hlc_charge_SRTCoincPulses').value
            f['srt_slc_charge'] = store.select('all_slc_charge_SRTCoincPulses').value
        except:
            f['srt_hlc_count']  = np.zeros(len(f['twc_hlc_count']))
            f['srt_slc_count']  = np.zeros(len(f['twc_hlc_count']))
            f['srt_nchannel']   = np.zeros(len(f['twc_hlc_count']))
            f['srt_hlc_charge'] = np.zeros(len(f['twc_hlc_count'])) 
            f['srt_slc_charge'] = np.zeros(len(f['twc_hlc_count']))

        tr          = np.greater(f['srt_hlc_count'],0)
        f['counts']   = tr*f['srt_hlc_count']+tr*f['srt_slc_count'] + np.invert(tr)*f['twc_hlc_count']+np.invert(tr)*f['twc_slc_count']
        f['nchannel'] = tr*f['srt_nchannel'] + np.invert(tr)*f['twc_nchannel']
        f['charges']  = tr*f['srt_hlc_charge']+tr*f['srt_slc_charge'] + np.invert(tr)*f['twc_hlc_charge']+np.invert(tr)*f['twc_slc_charge']

        if isMC:

            f['primary_x']        = store.select('MCPrimary').x
            f['primary_y']        = store.select('MCPrimary').y
            f['primary_z']        = store.select('MCPrimary').z
            f['primary_azi']      = store.select('MCPrimary').azimuth
            f['primary_zen']      = store.select('MCPrimary').zenith
            f['primary_E']        = store.select('MCPrimary').energy

            energy       = store.select('MCPrimary').energy
            f['weights'] = get_weights(set_name,energy, f['Nstations'])

            ###  Calculated Keys ### 
            laputop_x     = np.sin(f['laputop_zen'])*np.cos(f['laputop_azi'])
            laputop_y     = np.sin(f['laputop_zen'])*np.sin(f['laputop_azi'])
            laputop_z     = np.cos(f['laputop_zen'])
            primary_pos_x = f['primary_x']
            primary_pos_y = f['primary_y']
            primary_x     = np.sin(f['primary_zen'])*np.cos(f['primary_azi'])
            primary_y     = np.sin(f['primary_zen'])*np.sin(f['primary_azi'])
            primary_z     = np.cos(f['primary_zen'])

            f['opening_angle']    =  np.degrees(np.arccos(laputop_x*primary_x +
                                                laputop_y*primary_y +
                                                laputop_z*primary_z))
            f['lap_core_diff']    =  np.sqrt((primary_pos_x - laputop_x)**2 +
                                         (primary_pos_y - laputop_y)**2)
        if np.any(~np.equal(np.array([len(f[key]) for key in f.keys()]), len(f['counts']))):
            print('NOT EQUAL!')
            print(np.array([len(f[key]) for key in f.keys()]))
            err += 1
            err_list.append(fname)
            continue
        for key in f.keys():
            if i == 0:
                dataframe_dict[key] = f[key].tolist()
            else:
                dataframe_dict[key] += f[key].tolist()
        store.close()

        if i%50 == 0:
            print(i)
    df = pd.DataFrame.from_dict(dataframe_dict)
    df.to_hdf(outFile, 'dataframe', mode='w')
    print('Time taken: {}'.format(time.time() - t_sim))
    print('Time per file: {}\n'.format((time.time() - t_sim) / len(file_list)))
    print('%s total error files' % err)

    return

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Rewrite HDF files for analysis purposes',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dataset',
            help='Set to run over')
    p.add_argument('--isMC', action="store_true", default = False, dest='isMC',
            help='Is this simulation')
    args = p.parse_args()
    
    file_list  = glob.glob('/data/user/zgriffith/pev_photons/datasets/'+args.dataset+'/*.hdf5')
    #outFile = '/data/user/zgriffith/pev_photons/datasets/'+args.dataset+'.hdf5'
    outFile = '/data/user/zgriffith/pev_photons/resources/datasets/level3/2012_mc_qgs.hdf5'

    print(len(file_list))
    a = 0
    '''
    for i, file in enumerate(file_list):
        try:
            f = tables.openFile(file)
            f.root.IT73AnalysisIceTopQualityCuts.cols.IceTop_StandardFilter[:]
            f.close()
        except:
            print(file)
            file_list.remove(file)
            a += 1
    print(a)
    '''
    rewrite(file_list, outFile, args.dataset, args.isMC)
