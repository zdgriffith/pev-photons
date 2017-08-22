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
plt.style.use('stefan')
fig_dir = get_fig_dir()
colors = mpl.rcParams['axes.color_cycle']

def effective_area(E, label, fname, w):

    weights = []
    for i in E:
        if i < 6:
            weights.append(np.pi*.800**2) 
        elif i<7 and i> 6:
            weights.append(np.pi*1.100**2) 
        else:
            weights.append(np.pi*1.400**2) 

    bin_width  = 0.1
    E_hist     = dashi.factory.hist1d(E, np.arange(5,8.1,bin_width), weights = np.array(weights)*w**-1)
    error_hist = dashi.factory.hist1d(E, np.arange(5,8.1,bin_width), weights = w**-1*np.array(weights)**2)

    if fname in ['12622']:
        n_gen = 60000 #default
    else:
        events = np.load('/data/user/zgriffith/sim_files/'+fname+'_events.npy')
        n_gen  = events[:].astype('float')

    area  = E_hist.bincontent/n_gen
    error = np.sqrt(error_hist.bincontent)/n_gen
    ax0.errorbar(E_hist.bincenters, np.array(area), xerr = bin_width/2.,
                yerr = error, label = label,
                capsize = 0, lw = 2, capthick = 2, fmt = 'o', marker = 'o', ms = 0)

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
            
        vals, bins = effective_area(np.log10(f['primary_E']), labels[i], fname, w)
        comp.append(np.array(vals))

    for i, c in enumerate(comp):
        ratio = c/comp[1] 
        ax1.step(bins,np.append(ratio[0],ratio), color = colors[i])

    ax0.xaxis.set_visible(False)
    ax0.set_xlim([5.5,8])
    ax1.set_xlim([5.5,8])
    ax1.set_ylim([0,1.2])
    ax1.grid(b=True, color='grey', linestyle='dashed', alpha = 1)
    ax1.set_xlabel(r'log(E$_{\textrm{true}}$/GeV)', fontsize = 14)
    ax0.set_ylabel('Effective Area (km$^2$)', fontsize = 14)
    ax1.set_ylabel('Ratio to 2012', fontsize = 14)
    ax0.legend(loc = 'lower right')
    plt.savefig(fig_dir+args.outFile, facecolor='none', dpi=300)
    plt.close()
