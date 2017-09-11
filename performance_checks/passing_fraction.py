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
       
def passing_fraction(args):


    labels    = ['Data', 'Gamma Ray MC (E$^{-2.0}$ weighted)']
    bin_width = 0.1

    index = 0
    for year in args.years:
        l3_data, l3_sim = load_all_folds(year = year, or_cut = 0)
        if year == '2015':
            l4_data, l4_sim = load_all_folds(year = year, or_cut = 0.72)
        else:
            l4_data, l4_sim = load_all_folds(year = year, or_cut = 0.7)
        for j, label in enumerate(labels):
            if 'Data' in label:
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

            plt.step(energy_hist.binedges, np.append(energy_percent[0],energy_percent), color = colors[index], label = year+' '+label, ls = '-')
            plt.errorbar(energy_hist.binedges[:-1]+bin_width/2., energy_percent, yerr = error, fmt = 'none', color = colors[index], ecolor = colors[index], ms = 0)
            index += 1

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
    p = argparse.ArgumentParser(
            description='Create an all sky TS map',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'passing_vs_energy.png',
                   help    = 'file name')
    p.add_argument('--years', dest='years', type = str, nargs='+',
                   help='Year(s) to plot.  If \"all\", will plot the combination', default = ['2012'])
    args = p.parse_args()

    passing_fraction(args)
