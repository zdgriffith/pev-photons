#!/usr/bin/env python

########################################################################
# Plot the galactic plane upper limit
########################################################################

import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import interpolate

from utils.support import resource_dir, plot_style, fig_dir
    
def plot_limit(exp):
    ax.scatter(exp['E_0'], exp['flux'],
               marker=exp['marker'], label=exp['label'],
               color=exp['color'], zorder=2, s=50)
    ax.plot(np.full(2, exp['E_0']),
            np.full(2, exp['flux'])*[1, 0.7],
            color=exp['color'], zorder=2)
    ax.scatter(exp['E_0'], exp['flux']*0.7,
               color=exp['color'],
               marker="v", zorder=2, s=40)

def plot_range(exp):
    x = np.linspace(exp['E_min'], exp['E_max'], 100)
    y = exp['flux']*(exp['E_0']/x)**(3.0-2.0)
    ax.plot(x, y, ls='--', color=exp['color'])

def plot_flux_model(x, y0, y1, color, edgecolor, alpha, label):
    ax.fill_between(x, y0, y1,
                    edgecolor=edgecolor, color=color, alpha=alpha,
                    zorder=1)
    p = plt.Rectangle((0, 0), 0, 0,
                      edgecolor=edgecolor, facecolor=color,
                      label=label)
    ax.add_patch(p)

def plot_HESE():
    surv = np.loadtxt(resource_dir+'gamma_survival_vs_energy.txt')
    surv = surv.T
    spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0]*10**-12, surv[1], k=2)
    E = 10**(np.arange(-0.01, 5.01, 0.001))

    ratio = spline(E)
    phi0 = 0.2*(2*np.pi)*0.84e-8
    phi = phi0*np.ones(len(E))
    phi *= np.exp(-E/(6.*10**3))
    ax.plot(E,ratio*phi, label='HESE 4-year (fixed to E$^{-2.0}$)', color=colors[4], zorder = -1)

if __name__ == "__main__":
    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    fig, ax = plt.subplots()
    exp = {}
    exp['IC_Fermi'] = {'E_0': 2e3, 'E_min': 0.683e3, 'E_max': 2.73e3,
                       'flux': 1.044e-9, # GeV cm^-2 s^-1
                       'label': 'IceCube 5-year (Fermi Template)',
                       'marker':'s', 'color': colors[2]}
    exp['IC_Ingleman'] = {'E_0': 2e3, 'E_min': 0.683e3, 'E_max': 2.73e3,
                          'flux': 6.16e-10, # GeV cm^-2 s^-1
                          'label': 'IceCube 5-year (Ingleman-Thunman Template)',
                          'marker':'D', 'color': colors[1]}

    for key in exp:
        plot_limit(exp[key])
        plot_range(exp[key])

    # Model prediction for flux emission over our entire FOV
    xnew, unatt_low_y, att_low_y, unatt_up_y, att_up_y = np.loadtxt(resource_dir+'diffuse_disk_icecube_from_vernetto.dat').T

    plot_flux_model(xnew, unatt_low_y, unatt_up_y,
                    color='none', edgecolor='b', alpha=1.0,
                    label='Vernetto \& Lipari\'17 (Unattenuated)')

    plot_flux_model(xnew, att_low_y, att_up_y,
                    color='c', edgecolor='none', alpha=0.5,
                    label='Vernetto \& Lipari\'17 (Attenuated)')

    ax.set_xlim([10,1e4])
    ax.set_ylim([1e-11,1e-8])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$E_\gamma$ [TeV]')
    ax.set_ylabel(r'$E^2 \Phi$ [GeV cm${}^{-2}$ s${}^{-1}$]')
    ax.legend(loc='lower left', scatterpoints=1)
    plt.savefig(fig_dir+'galactic_plane/flux_scaled_to_gp_frac_vernetto.png')
    plt.close()
