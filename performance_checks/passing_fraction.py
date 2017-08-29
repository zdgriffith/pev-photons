#!/usr/bin/env python
import sys, os
sys.path.append(os.path.expandvars("$HOME"))
import dashi
dashi.visual()

import numpy as np
import matplotlib.pyplot as plt
plt.style.use('stefan')
import matplotlib as mpl
colors = mpl.rcParams['axes.color_cycle']

from support_functions import cut_maker, get_fig_dir, hits_llh_cutter, plot_setter
from support_pandas import load_all_folds
fig_dir = get_fig_dir()
       
def passing_fraction():

    l3_data, l3_sim = load_all_folds(year = '2012', or_cut = 0)
    l4_data, l4_sim = load_all_folds(year = '2012', or_cut = 0.7)

    sets      = ['burn_2012', '12533']
    labels    = ['Data', 'Gamma Ray MC (E$^{-2.0}$ weighted)']
    bin_width = 0.1

    for j, fname in enumerate(sets):
        if 'burn' in fname:
            l3 = l3_data
            l4 = l4_data
        else:
            l3 = l3_sim
            l4 = l4_sim

        bin_vals         = np.arange(5.7,8.1,bin_width)
        energy_hist      = dashi.factory.hist1d(np.log10(l3['laputop_E']), bin_vals)
        energy_kept_hist = dashi.factory.hist1d(np.log10(l4['laputop_E']), bin_vals)
        bin_num          = len(bin_vals) - 1
        passed           = energy_hist.bincontent-energy_kept_hist.bincontent
        energy_percent   = np.zeros(bin_num)
        error            = np.zeros(bin_num)

        #error formulation which avoids forbidden space - see Ullrich and Xu 2008
        #"Treatment of Errors in Efficiency Calculations" eqn 19.
        for i in range(bin_num):
            k = np.float(passed[i])
            n = np.float(energy_hist.bincontent[i])
            energy_percent[i] = energy_kept_hist.bincontent[i]/float(energy_hist.bincontent[i])
            error[i]          = np.sqrt(((k+1)*(k+2))/((n+2)*(n+3)) - ((k+1)**2)/((n+2)**2))

        plt.step(energy_hist.binedges, np.append(energy_percent[0],energy_percent), color = colors[j], label = labels[j], ls = '-')
        plt.errorbar(energy_hist.binedges[:-1]+bin_width/2., energy_percent, yerr = error, fmt = 'none', color = colors[j], ecolor = colors[j], ms = 0)

    plt.xlim([5.7,8])
    plt.xlabel('log(E/GeV)',fontweight='bold', fontsize = 24)
    plt.yscale('log', fontsize='24')
    plt.ylabel('Passing Fraction',fontweight='bold')
    l = plt.legend(loc = 'lower left', fontsize = 18, prop={'weight':'bold'})
    plot_setter(plt.gca(),l)
    plt.tight_layout()
    plt.savefig(fig_dir+'/passing_vs_energy.png', facecolor = 'none', dpi=300)
    plt.close()

if __name__ == "__main__":
    passing_fraction()
