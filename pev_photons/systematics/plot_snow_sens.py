#!/usr/bin/env python

########################################################################
# 
########################################################################

import argparse
import numpy as np
import matplotlib.pyplot as plt
from glob import glob

from pev_photons.utils.support import prefix, resource_dir
from pev_photons.utils.support import fig_dir, plot_setter, plot_style

if __name__ == "__main__":
    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios':[3, 1]})

    years = {'2011': [np.nan, '2011', '2012'],
             '2012': ['2011', '2012', '2013'],
             '2013': ['2012', '2013', '2014'],
             '2014': ['2013', '2014', '2015'],
             '2015': ['2014', '2015', np.nan]}

    lower = []
    upper = []
    standard = []
    for i, year in enumerate(['2011','2012','2013','2014','2015']):
        for snow_year in years[year]:
            if snow_year is np.nan:
                continue
            else:
                sens = np.load(prefix+'systematics/{}_sens_{}_snow.npy'.format(year, snow_year))
                if int(snow_year) == int(year):
                    standard.append([i, sens])
                elif int(snow_year) > int(year):
                    upper.append([i, sens])
                else:
                    lower.append([i, sens])

    labels = ['next year snow', 'same year snow', 'previous year snow']
    markers = ['v', '+', '^']
    for i, pairs in enumerate([upper, standard, lower]):
        pairs = np.array(pairs)
        ax0.plot(pairs.T[0], pairs.T[1]*1e3, marker=markers[i], label=labels[i], ls='none', ms=6)
        if i == 0:
            ax1.plot(pairs.T[0], pairs.T[1]/np.array(standard[0:4]).T[1],
                     marker=markers[i], ls='none', ms=6, color=colors[i])
        elif i == 2:
            ax1.plot(pairs.T[0], pairs.T[1]/np.array(standard[1:5]).T[1], marker=markers[i],
                     ls='none', ms=6, color=colors[i])
        else:
            ax1.axhline(y=1, color=colors[1])

    ax0.set_xticklabels([])
    ax0.set_ylim([4e-20, 2e-19])
    ax0.set_ylabel('Flux [cm$^{-2}$s$^{-1}$TeV$^{-1}$]')
    ax0.set_yscale('log')
    l = ax0.legend(loc='upper left')
    plot_setter(plt.gca(),l)
    ax0.set_xlim([-1, 5])
    ax1.set_xlim([-1, 5])
    ax1.set_xlabel(r'Declination [$^{\circ}$]')
    ax1.set_xticklabels(['', '2011','2012','2013','2014','2015', ''])
    ax1.set_ylim([0.4, 1.3])
    ax1.set_ylabel('Ratio', fontsize=14)
    ax1.set_yticks([0.4, 0.6, 0.8, 1.0, 1.2])
    ax1.set_yticklabels([0.4, 0.6, 0.8, 1.0, 1.2], fontsize=10)
    ax1.grid(alpha=0.2)
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/snow_height_sens.pdf')
    plt.close()
