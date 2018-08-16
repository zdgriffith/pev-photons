#!/usr/bin/env python

########################################################################
# Combine HDF files into a single Pandas dataframe for analysis
########################################################################

import os
import argparse
import time
import glob
import numpy as np
import pandas as pd

from pev_photons.utils.support import prefix

def check_testing(x, y, E, events):
    a = np.any((np.isclose(events['primary_x'].values[:,np.newaxis],x)
                & np.isclose(events['primary_y'].values[:,np.newaxis],y)
                & np.isclose(events['primary_E'].values[:,np.newaxis],E)), axis=0)
    return a

def get_weights(sim, energy):
    """ Create the MC weights for the given dataset generation parameters """

    def norm(emin, emax, eslope):
        #Function from weighting project
        if eslope < -1:
            g = eslope+1
            return (emax**g - emin**g)/g
        else:
            return np.log(emax/emin)

    def int_area(E, theta_max):
        #Integrated Area times Solid Angle
        radius = (800*np.greater_equal(E, 10**5)
                  + 300*np.greater_equal(E,10**6)
                  + 300*np.greater_equal(E,10**7))

        return ((radius*100)**2)*(1-np.cos(np.radians(theta_max))**2)*np.pi**2
    
    events = np.load('/data/user/zgriffith/sim_files/'+sim+'_events.npy') 

    def n_thrown(E):
        # Number of thrown events in an Ebin, normed by the size of the Ebin
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
    return weights

def rewrite(file_list, outFile, set_name, isMC, systematics):

    dataframe_dict = {}
    t_sim = time.time()
    err   = 0

    for i, fname in enumerate(file_list):
        print(i)
        f = {}
        try:
            store = pd.HDFStore(fname)
            f['mjd_time'] = store.select('I3EventHeader').time_start_mjd
        except:
            print('error, skipping')
            err += 1
            continue

        #f['mjd_time'] = store.select('I3EventHeader').time_start_mjd

        recos = ['Laputop']
        if systematics:
            recos += ['LaputopLambdaUp', 'LaputopLambdaDown',
                      'LaputopS125Up', 'LaputopS125Down']
        for reco in recos:
            f[reco+'_azimuth'] = store.select(reco).azimuth
            f[reco+'_zenith'] = store.select(reco).zenith
            f[reco+'_s125'] = store.select(reco+'Params').s125
            f[reco+'_E'] = store.select(reco+'_E').value
            for alpha in [2.0, 2.7, 3.0]:
                key = reco+'_alpha_{}_score'.format(alpha)
                f[key]= store.select(key).value
            if isMC:
                f[reco+'_opening_angle'] = store.select(reco+'_opening_angle').value

        if isMC:
            f['primary_azi'] = store.select('MCPrimary').azimuth
            f['primary_zen'] = store.select('MCPrimary').zenith
            f['primary_E']   = store.select('MCPrimary').energy

            energy = store.select('MCPrimary').energy
            f['weights'] = get_weights(set_name, energy)

        for key in f.keys():
            if i == 0:
                dataframe_dict[key] = f[key].tolist()
            else:
                dataframe_dict[key] += f[key].tolist()
        store.close()

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
            help='The dataset with which to create a dataframe.')
    p.add_argument('--isMC', action="store_true", default = False, dest='isMC',
            help='Is this simulation?')
    p.add_argument('--systematics', action="store_true", default = False, dest='systematics',
            help='Is this a systematics set?')
    args = p.parse_args()
    
    if args.systematics:
        file_prefix = prefix+'datasets/systematics/'
    else:
        file_prefix = prefix+'datasets/'
    if args.isMC:
        file_list = glob.glob(os.path.join(file_prefix, args.dataset, '*.hdf5'))
    else:
        file_list = glob.glob(os.path.join(file_prefix, 'data', args.dataset, '*.hdf5'))

    outFile = os.path.join(file_prefix, args.dataset+'.hdf5')
    rewrite(file_list, outFile, args.dataset, args.isMC, args.systematics)
