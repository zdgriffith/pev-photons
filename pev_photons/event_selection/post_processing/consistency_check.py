#!/usr/bin/env python

########################################################################
# 
########################################################################

import pandas as pd
import numpy as np
from sklearn.externals import joblib

from pev_photons.utils.support import prefix

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


    files = ['2012_mc.hdf5', '2012_mc_qgs.hdf5']
    for fname in files:
        mc = pd.read_hdf(prefix+'resources/datasets/level3/'+fname)

        cut = mc['standard_filter_cut']&mc['beta_cut']&mc['laputop_cut']
        cut = cut&mc['Q_cut']&mc['loudest_cut']&np.greater_equal(mc['Nstations'],5)
        cut = cut&np.isfinite(mc['llh_ratio'])&np.less_equal(mc['laputop_zen'], np.arccos(0.8))
        cut = cut&np.less_equal(mc['laputop_it'], 1)&np.greater_equal(mc['s125'], 10**-0.25)

        if 'qgs' in fname:
            out = 'qgs'
        else:
            out = 'sybll'
            np.random.seed(1337)
            training_fraction = 0.8
            cut = cut&~np.random.choice(2,len(mc['laputop_E']),p=[1-training_fraction, training_fraction])

        mc = mc[cut]
        mc['Laputop_azimuth'] = mc['laputop_azi']
        mc['Laputop_zenith'] = mc['laputop_zen']
        mc['Laputop_E'] = mc['laputop_E']
        mc['Laputop_opening_angle'] = np.radians(mc['opening_angle'])
        
        mc.to_hdf(prefix+'datasets/systematics/hadronic_models/2012/'+out+'_quality.hdf5', 'dataframe', mode='w')
        ps = prediction(mc, 'ps', '2012', 0.7)
        ps.to_hdf(prefix+'datasets/systematics/hadronic_models/2012/'+out+'_ps.hdf5', 'dataframe', mode='w')
        gal = prediction(mc, 'galactic', '2012', 0.7)
        gal.to_hdf(prefix+'datasets/systematics/hadronic_models/2012/'+out+'_diffuse.hdf5', 'dataframe', mode='w')
