#!/usr/bin/env python

########################################################################
# Plot the angular resolution of gamma-ray MC for set years.
########################################################################

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from support_functions import cut_maker, get_fig_dir, find_nearest, plot_setter

plt.style.use('stefan')
fig_dir = get_fig_dir()

def sigma(y):
    values, base = np.histogram(y, bins=np.arange(0,20,0.01),
                                weights=[1/float(len(y))]*len(y))
    cumulative = np.cumsum(values)

    for i, val in enumerate(cumulative):
        if val >= 0.68:
            return base[i]/1.51

def error(f, label, key, x_bins):
    bin_size = x_bins[1]-x_bins[0]

    if key in ['laputop_E', 'primary_E']:
        vals = np.log10(f[key]) 
    else:
        vals = f[key]

    bin_sigmas, bin_edges, n = stats.binned_statistic(vals,
                                                      f['opening_angle'],
                                                      statistic=sigma,
                                                      bins=x_bins)
    bin_center = bin_edges[:-1] + bin_size/2.

    sigmas = [bin_sigmas[find_nearest(bin_center, val)] for val in vals]
    
    avg = np.average(sigmas, weights=f['weights']*f['primary_E']**-2.0)
    plt.step(bin_edges, np.append(bin_sigmas[0], bin_sigmas),
             label=label+r', $\langle\sigma\rangle$ = %.2f$^{\circ}$' % avg)

    return np.radians(sigmas)

if __name__ == "__main__":
    
    cut_args = {'standard':1, 'laputop_it':1}
    
    sets = [cut_maker('12622',cut_args), cut_maker('12533', cut_args),
            cut_maker('12612', cut_args), cut_maker('12613', cut_args),
            cut_maker('12614', cut_args)]
    labels = ['2011', '2012', '2013', '2014', '2015']
    E_bins = np.arange(5.7,8.1, 0.10)

    for i, f in enumerate(sets):
        #Only plot first and last for simplicity
        if i in [0,4]:
            error(f, labels[i], 'primary_E', E_bins)

    plt.xlabel(r'log(E$_{\textrm{true}}$/GeV)')
    plt.xlim([5.7,8])
    plt.ylabel('Angular Resolution [$^{\circ}$]')
    l = plt.legend()
    plot_setter(plt.gca(), l)
    plt.tight_layout()
    plt.savefig(fig_dir+'ang_res_years.png', facecolor='none', dpi=300)
    plt.savefig('/home/zgriffith/public_html/paper/ang_res_years.pdf')
    plt.close()
