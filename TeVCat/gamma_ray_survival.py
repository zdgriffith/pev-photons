#!/usr/bin/env python

#==============================================================================
# File Name     : gamma_ray_survival.py
# Description   : Plots the survival function(s) for gamma rays 
# Creation Date : 09-07-2017
# Last Modified : Mon 11 Sep 2017 11:33:07 AM CDT
# Created By    : Zach Griffith 
#==============================================================================

import argparse, scipy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from support_functions import get_fig_dir, plot_setter
fig_dir = get_fig_dir()
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']

def survival_vs_energy(args):
    surv = np.loadtxt(args.prefix+'TeVCat/survival.txt')
    surv = surv.T
    spline = scipy.interpolate.InterpolatedUnivariateSpline(surv[0], surv[1], k=2)
    x = 10**np.arange(12,17, 0.01)
    plt.scatter(surv[0],surv[1])
    plt.plot(x,spline(x), label = 'spline fit')

    plt.legend()
    plt.xlabel('Energy [eV]', fontweight='bold')
    plt.ylabel('Survival Probability', fontweight='bold')
    plt.xscale('log')
    plt.tight_layout()
    plt.savefig(fig_dir+'survival.pdf')
    plt.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    args = p.parse_args()

    survival_vs_energy(args)
