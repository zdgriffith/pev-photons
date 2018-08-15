#!/usr/bin/env python

########################################################################
# Random Forest score distributions for interaction models
########################################################################

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from sklearn.externals import joblib

from pev-photons.utils.support import prefix, resource_dir, fig_dir, plot_setter, plot_style

def prediction(f, year):
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
            feature = np.log10(f[key].values)
        elif key == 'laputop_zen':
            feature = np.sin(f[key].values - np.pi/2.)
        else:
            feature = f[key].values

        if i == 0:
            features = feature
        else:
            features = np.column_stack((features,feature))

    f['alpha_2.0_score'] = hard_trainer.predict_proba(features).T[1]
    f['alpha_2.7_score'] = soft_trainer.predict_proba(features).T[1]
    f['alpha_3.0_score'] = trainer_3.predict_proba(features).T[1]

    return f

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='RF Probability Distribution',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', dest='year', type = str,
            help='Year', default = '2012')
    p.add_argument('-a', '--alpha', dest='alpha', type = float,
            help='Spectral Index', default = 2.0)
    p.add_argument('--k', dest='k', type = int,
            default = 5, help='Total cross val folds')
    args = p.parse_args()
    plt.style.use('gamma_rays_5yr')

    gammas = pd.read_hdf(prefix+'datasets/systematics/2012_sybll_quality.hdf5')
    qgs = pd.read_hdf(prefix+'datasets/systematics/2012_qgs_quality.hdf5')

    alpha = 2.0
    bins = np.arange(0,1.05,0.05)
    labels = ['SYBLL', 'QGS-JET']
    for i, df in enumerate([gammas, qgs]):
        mask = np.greater(np.log10(df['laputop_E']),6.0) & np.less(np.log10(df['laputop_E']),6.1)
        df = prediction(df, '2012')
        df = df[mask]
        dist = np.histogram(df['alpha_{}_score'.format(alpha)], bins=bins,
                            weights=np.full(len(df['alpha_2.0_score']), 1/float(len(df['alpha_2.0_score']))))[0]
        plt.step(bins, np.append(dist[0], dist), label = labels[i])

    plt.xlabel('Classifier Signal Probability')
    plt.ylabel('Density')
    plt.title('6.0 $<$ log10($E_{MC}$/GeV) $<$ 6.1')
    plt.xlim([0,1])
    plt.ylim([1e-4,1])
    plt.yscale('log')
    l = plt.legend(loc='lower right')
    plot_setter(plt.gca(), l)
    plt.tight_layout()
    plt.savefig(fig_dir+'event_selection/signal_probs.png')
    plt.close()
