#!/usr/bin/env python 

########################################################################
# comparing the passing fraction of interaction models.
########################################################################

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pev-photons.utils.support import prefix, resource_dir, fig_dir, plot_setter, plot_style
from sklearn.externals import joblib

def plot_fraction(level3, level4, label):
    bin_width = 0.1
    bin_vals = np.arange(5.7,8.1,bin_width)

    l3_hist, l3_edges = np.histogram(np.log10(level3['laputop_E'].values), bin_vals,
                                     weights=(level3['primary_E'].values**-2.0)*level3['weights'].values)
    l4_hist, l4_edges = np.histogram(np.log10(level4['laputop_E'].values), bin_vals,
                                     weights=(level4['primary_E'].values**-2.0)*level4['weights'].values)


    l3_counts, l3_edges = np.histogram(np.log10(level3['laputop_E'].values), bin_vals)
    l4_counts, l4_edges = np.histogram(np.log10(level4['laputop_E'].values), bin_vals)
    #passed = l3_hist-l4_hist
    passed = l3_counts-l4_counts

    # An error formulation which avoids forbidden space.
    # See Ullrich and Xu 2008:
    # "Treatment of Errors in Efficiency Calculations" eqn 19.
    bin_num = len(passed)
    error = np.zeros(bin_num)
    percent = np.zeros(bin_num)
    for i in range(bin_num):
        k = np.float(passed[i])
        n = np.float(l3_counts[i])
        percent[i] = l4_hist[i]/float(l3_hist[i])
        error[i] = np.sqrt(((k+1)*(k+2)) / ((n+2)*(n+3))
                           - ((k+1)**2) / ((n+2)**2))

    lines = ax0.step(l3_edges, np.append(percent[0],percent),
                     label=label, ls='-', zorder=-1)
    lc = lines[0].get_color()
    ax0.errorbar(l3_edges[:-1]+bin_width/2., percent,
                 yerr=error, fmt='none', color=lc,
                 ecolor=lc, ms=0, capthick=2, zorder=-1)

    return l3_edges, np.append(percent[0],percent), np.append(error[0], error)

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
            feature = np.log10(f[key].values)
        elif key == 'laputop_zen':
            feature = np.sin(f[key].values - np.pi/2.)
        else:
            feature = f[key].values

        if i == 0:
            features = feature
        else:
            features = np.column_stack((features,feature))

    if selection == 'point_source':
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
    p.add_argument('--cut_val', dest='cut_val', type = float,
                   default = 0.7, help = 'cut value for random forests')
    p.add_argument('--selection', type=str,
                   default='point_source', help='event selection')
    args = p.parse_args()

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

    years = ['2012']

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios':[3, 1]})

    comp = []
    models = ['sybll', 'qgs']
    labels = ['SYBLL 2.1', 'QGSJet-II 04']
    errors = []
    if args.selection == 'point_source':
        selection = 'ps'
    else:
        selection = 'gal'

    for i, model in enumerate(models):
        level3 = []
        level4 = []
        for j, year in enumerate(years): 
            gammas = pd.read_hdf(prefix+'datasets/systematics/{}_{}_quality.hdf5'.format(year, model))
            level3.append(gammas)
            passing_gammas = pd.read_hdf(prefix+'datasets/systematics/{}_{}_{}.hdf5'.format(year, model, selection))
            level4.append(passing_gammas)

        x, vals, error = plot_fraction(pd.concat(level3), pd.concat(level4),
                                       label=labels[i])
        comp.append(vals)
        errors.append(error)

    for i, c in enumerate(comp):
        ratio = c/comp[0] 
        ax1.step(x, ratio, color=colors[i])
    
        ax1.fill_between(x, ratio+errors[i]/comp[i],
                         ratio-errors[i]/comp[i], step='pre',
                         color=colors[i], alpha=0.5)

    ax0.set_xticklabels([])
    ax0.set_xlim([5.7,8])
    ax0.set_ylim([0, 1])
    ax0.set_ylabel('Passing Fraction')
    l = ax0.legend(loc='lower right')
    plot_setter(ax0, l)

    ax1.set_xlim([5.7,8])
    ax1.set_ylim([0.6, 1.4])
    ax1.set_xlabel(r'log(E$_{\textrm{reco}}$/GeV)')
    ax1.set_ylabel('SYBLL Ratio', fontsize=12)
    ax1.set_yticks([0.7,0.8,0.9,1.0,1.1,1.2,1.3])
    ax1.set_yticklabels([0.7,0.8,0.9,1.0,1.1,1.2,1.3], fontsize=8)
    ax1.grid(alpha=0.2)
    fig.tight_layout()
    plt.savefig(fig_dir+'event_selection/model_test_%s.pdf' % args.selection)
    plt.close()
