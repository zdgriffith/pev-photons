#!/usr/bin/python

########################################################################
# Plot upper limits for a galactic plane flux.
########################################################################

import scipy
import numpy as np
import matplotlib.pyplot as plt

from pev_photons.support import prefix, resource_dir, fig_dir, plot_style

def abs(E):
    surv   = np.loadtxt(resource_dir+'gamma_survival_vs_energy.txt')
    surv   = surv.T
    return scipy.interpolate.InterpolatedUnivariateSpline(surv[0]*10**-12,
                                                          surv[1], k=2)(E)
    
# Plots an arrow
def plot_limit(x,y, unc = None, label = '', color = 'k'):
    # A scatter point.
    plt.scatter(x, y,
                zorder=1, s=30,
                color=color, marker="H",
                label=label)

    if unc:
        plt.errorbar(x, y, yerr=unc*y,
                     color=color,
                     markeredgewidth=1.5)

if __name__ == "__main__":

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']
    
    x = 2*10**6
    conv = (x**2)/(2*np.pi*0.2)
    fluxes = {
              'Fermi pi$^0$': (2.61e-22)*conv,
              '5$^{\circ}$ box': (3.42e-22)*conv,
              'Ingelman-Thunman': (1.54e-22)*conv}
              
    for i, key in enumerate(fluxes.keys()):
        plot_limit(x, fluxes[key], unc = 0.1,
                   label=key, color=colors[i])

    a = np.loadtxt(prefix+'galactic_plane/kra_gamma.txt')
    plt.plot(a.T[0]*1e3, a.T[1], label = 'KRA-gamma')
    plt.plot(a.T[0]*1e3, abs(a.T[0])*a.T[1], label = 'KRA-gamma (attenuated)')
    plt.xlim([1e0,1e8])
    plt.ylim([1e-10,1e-5])
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(r'$E_\gamma$ [GeV]')
    plt.ylabel(r'$E^2J_\gamma$ [GeV cm${}^{-2}$ s${}^{-1}$ sr${}^{-1}$]')
    plt.legend()
    plt.savefig(fig_dir+'galactic_plane/kra_comp.png', facecolor='none',
                bbox_inches="tight", dpi=300)
    plt.close()
