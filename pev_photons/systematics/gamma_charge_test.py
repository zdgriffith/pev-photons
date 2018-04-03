#!/usr/bin/env python 

########################################################################
# Examines the effect the magnitude of charge has on passing fraction
########################################################################

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pev_photons.utils.support import resource_dir, fig_dir, plot_setter, plot_style
from sklearn.externals import joblib

def plot_fraction(level3, level4, label):
    bin_width = 0.1
    bin_vals = np.arange(5.7,8.1,bin_width)

    l3_hist, l3_edges = np.histogram(np.log10(level3['laputop_E'].values), bin_vals,
                                     weights=(level3['primary_E'].values**-2.0)*level3['weights'].values)
    l4_hist, l4_edges = np.histogram(np.log10(level4['laputop_E'].values), bin_vals,
                                     weights=(level4['primary_E'].values**-2.0)*level4['weights'].values)

    passed = l3_hist-l4_hist

    # An error formulation which avoids forbidden space.
    # See Ullrich and Xu 2008:
    # "Treatment of Errors in Efficiency Calculations" eqn 19.
    bin_num = len(passed)
    error = np.zeros(bin_num)
    percent = np.zeros(bin_num)
    for i in range(bin_num):
        k = np.float(passed[i])
        n = np.float(l3_hist[i])
        percent[i] = l4_hist[i]/float(l3_hist[i])
        error[i] = np.sqrt(((k+1)*(k+2)) / ((n+2)*(n+3))
                           - ((k+1)**2) / ((n+2)**2))

    if '1.00' in label:
        lines = ax0.step(l3_edges, np.append(percent[0],percent),
                         label=label, ls='-', zorder=-1)
        lc = lines[0].get_color()
        ax0.errorbar(l3_edges[:-1]+bin_width/2., percent,
                     yerr=error, fmt='none', color=lc,
                     ecolor=lc, ms=0, capthick=2, zorder=-1)
    else:
        lines = ax0.step(l3_edges, np.append(percent[0],percent),
                         label=label, ls='-')

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


def plot_dists():

    fracs = []
    errors = []
    for i, param_val in enumerate(args.param_range):
        level3 = []
        level4 = []
        for year in args.years: 
            gammas = pd.read_hdf(resource_dir+'datasets/level3/'+year+'_mc_quality.hdf5')
            gammas[args.param] = param_val*gammas[args.param]
            passing_gammas = prediction(gammas, args.selection,
                                        year, args.cut_val)
            level3.append(gammas)
            level4.append(passing_gammas)

        E_bins, frac, error = plot_fraction(pd.concat(level3), pd.concat(level4),
                                            label='{:.2}*{}'.format(param_val, args.param_name))
        fracs.append(frac)
        errors.append(error)
        if param_val == 1.0:
            standard_index = i

    plot_uncertainty(E_bins, fracs, errors, standard_index)


def plot_uncertainty(E_bins, fracs, errors, standard_index):
    for i, frac in enumerate(fracs):
        ratio = frac/fracs[standard_index] 
        ax1.step(E_bins, ratio, color=colors[i])
    
    ax1.fill_between(E_bins,
                     1 - errors[standard_index]/fracs[standard_index],
                     1 + errors[standard_index]/fracs[standard_index],
                     step='pre', color=colors[standard_index], alpha=0.5)


if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Write exp and mc datasets using random forests',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--cut_val', dest='cut_val', type = float,
                   default = 0.7, help = 'cut value for random forests')
    p.add_argument('--param', type=str,
                   default='s125', help='Parameter key')
    p.add_argument('--param_name', type=str,
                   default='S$_{125}$', help='Parameter name')
    p.add_argument('--param_range', type=float, nargs='+',
                   default=[1.15, 1.00, 0.85],
                   help='Parameter values to test.')
    p.add_argument('--years', type=str, nargs='+',
                   default=['2011', '2012', '2013', '2014', '2015'],
                   help='Year(s) to include.')
    p.add_argument('--selection', type=str,
                   default='point_source', help='event selection')
    args = p.parse_args()

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios':[3, 1]})

    plot_dists()

    major_ticks = np.arange(6, 8.5, 0.5)
    ax0.set_xticks(major_ticks)
    ax0.set_xticklabels([])
    ax0.set_xlim([5.7,8])
    ax0.set_ylim([0.4, 1])
    ax0.set_ylabel('Passing Fraction')
    if args.selection == 'point_source':
        l = ax0.legend(loc='lower right')
    else:
        l = ax0.legend(loc='upper left')
    plot_setter(ax0, l)

    major_ticks = np.arange(6, 8.5, 0.5)
    ax1.set_xticks(major_ticks)
    major_ticks = np.arange(0.9, 1.15, 0.05)
    minor_ticks = np.arange(0.9, 1.11, 0.01)
    ax1.set_yticks(major_ticks)
    ax1.set_yticks(minor_ticks, minor=True)
    ax1.grid(which='minor', alpha=0.2, ls='--')
    ax1.grid(which='major', alpha=0.5)

    ax1.set_xlim([5.7,8])
    ax1.set_ylim([0.90, 1.10])
    ax1.set_xlabel(r'log(E$_{\textrm{reco}}$/GeV)')
    ax1.set_ylabel('Ratio')
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/%s_test_%s.pdf' % (args.param, args.selection))
    plt.close()
