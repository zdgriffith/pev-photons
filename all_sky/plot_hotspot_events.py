#!/usr/bin/env python

########################################################################
# Zoomed Region on hotspot location with events
########################################################################

import numpy as np
import matplotlib.pyplot as plt

from pev_photons.support import prefix, fig_dir, plot_style

from colormaps import cmaps

def plot_events():
    years = ['2011', '2012', '2013', '2014','2015']
    decs = []
    ras = []
    E_list = []
    for i, year in enumerate(years): 
        exp = np.load(prefix+'/datasets/'+year+'_exp_ps.npy')
        decs.extend(exp['dec'])
        ras.extend(exp['ra'])
        E_list.extend(exp['logE'])
        
    ra = np.degrees(np.array(ras))
    dec = np.degrees(np.array(decs))
    Es = np.array(E_list)
    mask = np.less(dec,-70)&np.greater(dec,-76)&np.less(ra, 152)&np.greater(ra, 145)
    logE = Es[mask]
    sc = plt.scatter(ra[mask],dec[mask], color='k',
                     c=logE, lw=0, cmap=cmaps['plasma'], s = 2**2)
    clb = plt.colorbar(sc, orientation='vertical')
    clb.set_label('logE', fontsize=20)

if __name__ == "__main__":
    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    plot_events()

    hotspot = np.load(prefix+'all_sky/hotspot.npy')
    plt.scatter(hotspot['ra'][0], hotspot['dec'][0],
                marker='+', color = 'green', s = 2**6)
    ax = plt.gca()
    ax.grid(color='k', alpha=0.2)
    ax.set_xlim([145,152])
    ax.set_ylim([-75,-70])

    ax.set_xlabel('RA [$^\circ$]')
    ax.set_ylabel('Dec [$^\circ$]')
    plt.savefig(fig_dir+'all_sky/hotspot_zoom.pdf')
    plt.close()
