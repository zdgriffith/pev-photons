#!/usr/bin/env python 

#######################################
####   Write Analysis Datasets   ######
#######################################

import argparse
import numpy as np
import pandas as pd

from support_pandas import cut_maker, construct_arr
from sklearn.externals import joblib

def prediction(f, selection, year, cut_val):
    hard_trainer = joblib.load('/data/user/zgriffith/rf_models/'+year+'/final/forest_2.0.pkl')
    soft_trainer = joblib.load('/data/user/zgriffith/rf_models/'+year+'/final/forest_2.7.pkl')
    trainer_3    = joblib.load('/data/user/zgriffith/rf_models/'+year+'/final/forest_3.0.pkl')

    feats = [
                'charges',
                'laputop_ic', 
                'llh_ratio',
                's125',
                'laputop_zen',
            ]

    for i, key in enumerate(feats):
        if key == 's125':
            feature = np.log10(f[key])
        elif key == 'laputop_zen':
            feature = np.sin(f[key] - np.pi/2.)
        else:
            feature = f[key]

        if i == 0:
            features = feature
        else:
            features = np.column_stack((features,feature))

    if selection == 'ps':
        alpha_2  = hard_trainer.predict_proba(features).T[1]
        alpha_27 = soft_trainer.predict_proba(features).T[1]
        cut      = np.greater(alpha_2,cut_val)|np.greater(alpha_27,cut_val)
    else:
        alpha_3 = trainer_3.predict_proba(features).T[1]
        cut      = np.greater(alpha_3,cut_val)

    return f[cut]

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Write exp and mc datasets using random forests',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--cut_val', dest='cut_val', type = float,
                   default = 0.7, help = 'cut value for random forests')
    args = p.parse_args()

    pf = '/data/user/zgriffith/datasets/'

    gamma_ratio = 0.2 # fraction of gamma dataset not used in training
    ang_res_sim = {'2011':'12622', '2012':'12533', '2013':'12612','2014':'12613', '2015':'12614'}

    years       = ['2011', '2012', '2013', '2014','2015']
    l3_sim_cuts = {'standard':1, 'laputop_it':1, 's125':10**(-0.25)}

    for i, year in enumerate(years): 
        data     = pd.read_hdf('/data/user/zgriffith/datasets/'+year+'.hdf5')
        sim      = cut_maker(ang_res_sim[year]+'_testing', l3_sim_cuts)
        for selection in ['ps', 'diffuse']:
            cut_sim      = prediction(sim, selection, year, args.cut_val)
            if selection == 'ps':
                cut_data = data[np.greater(data['alpha_2.0'], args.cut_val)|np.greater(data['alpha_2.7'], args.cut_val)]
            else:
                cut_data = data[np.greater(data['alpha_3.0'], args.cut_val)]
            exp, mc  = construct_arr(cut_data, cut_sim, testing_fraction = gamma_ratio, sim = ang_res_sim[year])
            np.save(args.prefix+'/datasets/'+year+'_exp_'+selection+'.npy', exp)
            np.save(args.prefix+'/datasets/'+year+'_mc_'+selection+'.npy', mc)
