#!/usr/bin/env python

########################################################################
# Plot the effective area for gamma rays as a function of zenith.
########################################################################

import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import dashi
import simFunctions
from support_pandas import cut_maker, get_fig_dir

dashi.visual()
plt.style.use('stefan')
fig_dir = get_fig_dir()
colors = mpl.rcParams['axes.color_cycle']

def effective_area(f, label, fname, args):

    weights = []
    for i in np.log10(f['primary_E']):
        if i < 6:
            weights.append(np.pi*0.800**2) 
        elif i<7 and i> 6:
            weights.append(np.pi*1.100**2) 
        else:
            if 'Protons' in label:
                weights.append(np.pi*1.700**2)
            else:
                weights.append(np.pi*1.400**2) 

    zen = np.cos(f['primary_zen'])
    bins = np.linspace(np.cos(np.radians(45.)),1, 15)
    hist = dashi.factory.hist1d(zen, bins, weights=weights)
    error_hist = dashi.factory.hist1d(zen, bins,
                                      weights=np.array(weights)**2)

    n_per_bin = 1.8e6/float(30*len(hist.bincontent))
    area = hist.bincontent/n_per_bin
    error = np.sqrt(error_hist.bincontent)/n_per_bin
    
    plt.errorbar(hist.bincenters, area,
                 xerr=(hist.binedges[1]-hist.binedges[0])/2.,
                 yerr=error, label=label,
                 capsize=0, lw=2, capthick=2, fmt='o',
                 marker='o', ms=0)

    return area, hist.binedges

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--outFile', type=str,
                   default='eff_area_zenith.png',
                   help='file name')
    args = p.parse_args()


    cut_args = {}
    f = cut_maker('12614', cut_args)
    f = f[np.greater(f['primary_E'], 10**6)&np.less(f['primary_E'], 10**6.1)]
    vals, bins = effective_area(f, '2015 Gamma Rays', '12614', args)

    plt.xlim([1,0.5])
    plt.xlabel('cos(MC Zenith)')
    plt.ylabel('Effective Area (km$^2$)')
    plt.axvline(x=np.cos(np.radians(45)),
                label='45 degrees',
                color=colors[1])
    plt.title('6.0 $<$ log(E$_{MC}$/GeV) $<$ 6.1')
    plt.legend()
    ax = plt.gca()
    plt.savefig(fig_dir+args.outFile, facecolor='none', dpi=300)
    plt.close()
