#!/usr/bin/env python

########################################################################
# Plot the effective area for gamma-ray simulation 
# over each of the 5 years used in the analysis
########################################################################

import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import dashi
from support_pandas import get_fig_dir
from support_functions import plot_setter

from load_datasets import load_level3_files
dashi.visual()
plt.style.use('stefan')
fig_dir = get_fig_dir()
colors = mpl.rcParams['axes.color_cycle']

def sigmoid_flat(energy, p0, p1, p2):
    return p0 / (1 + np.exp(-p1*np.log10(energy) + p2))

def sigmoid_slant(energy, p0, p1, p2, p3):
    return (p0 + p3*np.log10(energy)) / (1 + np.exp(-p1*np.log10(energy) + p2))

def get_effective_area_fit(energy_midpoints, eff_area,
                           eff_area_error, Ebin_width,
                           fit_func=sigmoid_slant, energy_points=None):

    energy_bins = 10**np.arange(5.0, 8.05, Ebin_width)
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

def effective_area(args, logE, year, w, color):

    weights = np.zeros(len(logE))
    for i, E in enumerate(logE):
        if E<6:
            weights[i] += np.pi*.800**2
        elif E<7 and E>6:
            weights[i] += np.pi*1.100**2
        else:
            weights[i] += np.pi*1.400**2

    bins = np.arange(5,8.1,args.Ebin_width)
    E_hist = dashi.factory.hist1d(logE, bins,
                                  weights=(w**-1)*weights)
    error_hist = dashi.factory.hist1d(logE, bins,
                                      weights=(w**-1)*weights**2)

    if year == '2011':
        n_gen = 60000
    else:
        events = np.load(args.prefix+'datasets/level3/'+year+'_mc_total_events.npy')
        n_gen  = events[:].astype('float')

    area = E_hist.bincontent/n_gen
    error = np.sqrt(error_hist.bincontent)/n_gen
    
    #Plot bins unless told not to
    if not args.noBins:
        line = ax0.errorbar(E_hist.bincenters, area,
                            xerr=args.Ebin_width/2., yerr=error,
                            capsize=0, capthick=2, lw=2, ms=0,
                            label=year, color=color, fmt='o', marker='o')
        year = None

    #Plot Sigmoid of Effective Area
    fine_bins = np.arange(5.7,8.01,0.01)
    if args.sigmoid:
        x = 10**fine_bins
        sigmoid = get_effective_area_fit(E_hist.bincenters, area,
                                         error, args.Ebin_width,
                                         fit_func=sigmoid_flat,
                                         energy_points=x)
        line = ax0.plot(fine_bins, sigmoid, color=color,
                        label=year)
        return sigmoid, fine_bins, line
    else:
        return area, bins, line[0]

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot the effective area for each MC year',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--outFile', default='effective_area_years.png',
                   help='file name')
    p.add_argument('--noBins', action='store_true', default=False,
                   help='if True, do not plot bins')
    p.add_argument('--sigmoid', action='store_true', default=False,
                   help='if True, plot sigmoid fit of eff area')
    p.add_argument('--Ebin_width', type=float, default = 0.1,
                   help='log(E/GeV) bin size')
    args = p.parse_args()

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios':[3, 1]})

    comp = []
    lines = []
    years = ['2011', '2012', '2013', '2014', '2015']
    for i, year in enumerate(years):
        f = pd.read_hdf(args.prefix+'datasets/level3/'+year+'_mc_quality.hdf5')

        # Reweight events with <8 stations triggered for 2011 due to filter
        if year == '2011':
            w = (2*(np.greater(f['Nstations'],3)&np.less(f['Nstations'],8))+1.)
        else:
            w = np.ones(len(f['Nstations']))
            
        vals, x, line = effective_area(args, np.log10(f['primary_E']),
                                       year, w, colors[i])
        comp.append(vals)
        lines.append(line[0])

    for i, c in enumerate(comp):
        ratio = c/comp[1] 
        ax1.plot(x, ratio, color=colors[i])

    ax0.set_xticklabels([])
    ax0.set_xlim([5.7,8])
    ax0.set_ylim([0,0.55])
    ax0.set_ylabel('Effective Area [km$^2$]')

    ax1.set_xlim([5.7,8])
    ax1.set_ylim([0.2,1.2])
    ax1.grid(b=True, color='grey')#, linestyle='dashed')
    ax1.set_xlabel(r'log(E$_{\textrm{\textsc{mc}}}$/GeV)')
    ax1.set_ylabel(r'A$_{\textrm{eff}}$/A$_{\textrm{eff}}$(2012)', fontsize=14)

    l = plt.figlegend(lines, years, loc='upper center', frameon=False,
                   bbox_to_anchor=(0.5,    # horizontal
                                   0.415), # vertical 
                   ncol=5, fancybox=False)
    plot_setter(plt.gca(),l)

    plt.savefig(fig_dir+args.outFile, facecolor='none', dpi=300)
    #plt.savefig('/home/zgriffith/public_html/paper/eff_area_comp.pdf')
    plt.close()
