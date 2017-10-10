#!/usr/bin/python

########################################################################
# Plot upper limits for a galactic plane flux.
########################################################################

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from support_functions import get_fig_dir

fig_dir = get_fig_dir()
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
    
# Plots an arrow
def plot_limit(x,y, unc = None, label = '', color = 'k'):
    # A scatter point.
    plt.scatter(x, y,
                zorder=1, s=30,
                color=color, marker="H",
                label=label)

    # A vertical line.
    plt.plot([x, x], [y, 0.33*y],
             zorder=0,
             color=color, linewidth=1.5,
             alpha=0.75)

    # The bottom triangle
    plt.scatter(x, 0.33*y,
                zorder=2, s=80, 
                color=color, marker="v",
                alpha=0.75)

    if unc:
        plt.errorbar(x, y, yerr=unc*y,
                     color=color,
                     markeredgewidth=1.5)

if __name__ == "__main__":
    
    x = 2*10**6
    conv = (x**2)/(2*np.pi*0.2)
    fluxes = {'Old Skylab (broken)': 3.79e-9,
              'Old Skylab (fixed)': 6.63665400875e-10,
              'Fermi pi$^0$': (2.47e-22)*conv,
              '5$^{\circ}$ box': (3.42e-22)*conv,
              'Ingelman-Thunman': (1.54e-22)*conv}
              
    for i, key in enumerate(fluxes.keys()):
        plot_limit(x, fluxes[key], unc = 0.1,
                   label=key, color=colors[i])

    plt.xlim([1e5,1e8])
    plt.ylim([3e-10,7e-9])
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(r'$E_\gamma$ [GeV]')
    plt.ylabel(r'$E^2J_\gamma$ [GeV cm${}^{-2}$ s${}^{-1}$ sr${}^{-1}$]')
    plt.legend()
    plt.savefig(fig_dir+'sensitivity_comparison.png', facecolor='none',
                bbox_inches="tight", dpi=300)
    plt.close()
