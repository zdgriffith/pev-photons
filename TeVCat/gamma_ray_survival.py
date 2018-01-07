#!/usr/bin/env python

########################################################################
# Plots the survival function(s) for gamma rays 
########################################################################

import scipy
import numpy as np
import matplotlib.pyplot as plt

from pev_photons.support import prefix, get_fig_dir, plot_style

def survival_vs_energy():
    surv = np.loadtxt(prefix+'TeVCat/gamma_survival_vs_energy.txt')
    surv = surv.T
    spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0], surv[1], k=2)
    x = 10**np.arange(12,17, 0.01)
    plt.scatter(surv[0],surv[1])
    plt.plot(x,spline(x), label = 'spline fit')

    plt.xlim([10**12,10**17])
    plt.ylim([0,1])
    plt.legend()
    plt.xlabel('Energy [eV]', fontweight='bold')
    plt.ylabel('Survival Probability', fontweight='bold')
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig(get_fig_dir()+'survival_vs_energy.pdf')
    plt.close()

def survival_vs_distance():
    surv = np.loadtxt(prefix+'TeVCat/gamma_survival_vs_distance.txt')
    surv = surv.T
    spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0], surv[1], k=2)
    x = np.arange(0,30, 0.01)
    plt.scatter(surv[0],surv[1])
    plt.plot(x,spline(x), label = 'spline fit')

    plt.xlim([0,30])
    plt.ylim([0,1])
    plt.legend()
    plt.xlabel('Distance to Sun [kpc]', fontweight='bold')
    plt.ylabel('Survival Probability', fontweight='bold')
    plt.tight_layout()
    plt.savefig(get_fig_dir()+'survival_vs_distance.pdf')
    plt.close()

def absorption_spline(E):
    surv   = np.loadtxt(prefix+'TeVCat/gamma_survival_vs_energy.txt')
    surv   = surv.T
    return scipy.interpolate.InterpolatedUnivariateSpline(surv[0]*10**-12,
                                                          surv[1], k=2)(E)

if __name__ == "__main__":

    plt.style.use(plot_style)

    survival_vs_energy()
    survival_vs_distance()
