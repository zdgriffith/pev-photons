#!/usr/bin/env python

##################################
###  Plot the effective area   ###
###  for gamma-ray simulation  ###
###  over each of the 5 years  ###
##################################

import argparse, sys, os, simFunctions
sys.path.append(os.path.expandvars("$HOME"))
import dashi
dashi.visual()
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from support_pandas import cut_maker, get_fig_dir
from scipy.optimize import curve_fit
plt.style.use('stefan')
fig_dir = get_fig_dir()
colors = mpl.rcParams['axes.color_cycle']

def sigmoid_flat(energy, p0, p1, p2):
    return p0 / (1 + np.exp(-p1*np.log10(energy) + p2))


def sigmoid_slant(energy, p0, p1, p2, p3):
    return (p0 + p3*np.log10(energy)) / (1 + np.exp(-p1*np.log10(energy) + p2))


def get_effective_area_fit(energy_midpoints, eff_area, eff_area_error, Ebin_width, fit_func=sigmoid_slant, energy_points=None):

    energy_bins      = 10**np.arange(5.0, 8.05, Ebin_width)
    energy_midpoints = (energy_bins[1:] + energy_bins[:-1]) / 2

    energy_min_fit, energy_max_fit = 5.7, 8.0
    midpoints_fitmask = np.logical_and(energy_midpoints > 10**energy_min_fit,
                                       energy_midpoints < 10**energy_max_fit)

    if fit_func.__name__ == 'sigmoid_flat':
        p0 = [1.5e5, 8.0, 50.0]
    elif fit_func.__name__ == 'sigmoid_slant':
        p0 = [1.4e5, 8.5, 50.0, 800]

    popt, pcov = curve_fit(fit_func,
                                energy_midpoints[midpoints_fitmask],
                                eff_area[midpoints_fitmask], p0=p0,
                                sigma=eff_area_error[midpoints_fitmask])

    return fit_func(energy_points, *popt)

def effective_area(E, label, fname, w, args, index):

    weights = []
    for i in E:
        if i < 6:
            weights.append(np.pi*.800**2) 
        elif i<7 and i> 6:
            weights.append(np.pi*1.100**2) 
        else:
            weights.append(np.pi*1.400**2) 

    E_hist     = dashi.factory.hist1d(E, np.arange(5,8.1,args.Ebin_width), weights = np.array(weights)*w**-1)
    error_hist = dashi.factory.hist1d(E, np.arange(5,8.1,args.Ebin_width), weights = w**-1*np.array(weights)**2)

    if fname in ['12622']:
        n_gen = 60000 #default
    else:
        events = np.load('/data/user/zgriffith/sim_files/'+fname+'_events.npy')
        n_gen  = events[:].astype('float')

    area  = E_hist.bincontent/n_gen
    error = np.sqrt(error_hist.bincontent)/n_gen
    
    #Plot bins unless told not to
    if not args.noBins:
        ax0.errorbar(E_hist.bincenters, np.array(area), xerr = args.Ebin_width/2.,
                    yerr = error, label = label,
                    capsize = 0, lw = 2, capthick = 2, fmt = 'o', marker = 'o', ms = 0, color = colors[index])

    #Plot Sigmoid of Effective Area
    if args.sigmoid:
        x = 10**np.arange(5.7,8.01,0.01)
        sigmoid = get_effective_area_fit(E_hist.bincenters, area, error, args.Ebin_width, fit_func=sigmoid_flat, energy_points = x)
        ax0.plot(np.log10(x), sigmoid, color = colors[index], label = label)

    return area, E_hist.binedges

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'effective_area_years.png',
                   help    = 'file name')
    p.add_argument('--noBins', dest='noBins', action = 'store_true',
            default = False, help='if True, do not plot bins')
    p.add_argument('--sigmoid', dest='sigmoid', action = 'store_true',
            default = False, help='if True, plot sigmoid fit of eff area')
    p.add_argument('--Ebin_width', dest='Ebin_width', type=float,
            default = 0.1, help='log(E/GeV) bin size')
    args = p.parse_args()

    labels  = ['Oct 2011', 'Oct 2012', 'Oct 2013', 'Nov 2014', 'Oct 2015']

    left  = 0.15
    width = 0.8
    ax0   = plt.axes([left, 0.36, width, 0.6])
    ax1   = plt.axes([left, 0.14, width, 0.19])

    comp     = []
    cut_args = {'standard':1, 'laputop_it':1}

    for i, fname in enumerate(['12622', '12533', '12612', '12613', '12614']):
        f   = cut_maker(fname, cut_args)
        if fname == '12622':
            w = (2*(np.greater(f['Nstations'],3)&np.less(f['Nstations'],8))+1.)
        else:
            w = np.ones(len(f['Nstations']))
            
        vals, bins = effective_area(np.log10(f['primary_E']), labels[i], fname, w, args, i)
        comp.append(np.array(vals))

    for i, c in enumerate(comp):
        ratio = c/comp[1] 
        ax1.step(bins,np.append(ratio[0],ratio), color = colors[i])

    ax0.xaxis.set_visible(False)
    ax0.set_xlim([5.7,8])
    ax1.set_xlim([5.7,8])
    ax0.set_ylim([0,0.55])
    ax1.set_ylim([0,1.2])
    ax1.grid(b=True, color='grey', linestyle='dashed', alpha = 1)
    ax1.set_xlabel(r'log(E$_{\textrm{true}}$/GeV)', fontsize = 14)
    ax0.set_ylabel('Effective Area (km$^2$)', fontsize = 14)
    ax1.set_ylabel('Ratio to 2012', fontsize = 14)
    ax0.legend(loc = 'lower right')
    plt.savefig(fig_dir+args.outFile, facecolor='none', dpi=300)
    plt.close()
