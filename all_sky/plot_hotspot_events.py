#!/usr/bin/env python

########################################################################
# Zoomed Region on a particular location with events
########################################################################

import argparse
import copy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

import healpy as hp
from support_functions import get_fig_dir

from matplotlib import cm

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()
from colormaps import cmaps

def plot_events(pf):
    years = ['2011', '2012', '2013', '2014','2015']
    decs = []
    ras = []
    E_list = []
    for i, year in enumerate(years): 
        exp = np.load(pf+'/datasets/'+year+'_exp_ps.npy')
        decs.extend(exp['dec'])
        ras.extend(exp['ra'])
        E_list.extend(exp['logE'])
        
    ra = np.degrees(np.array(ras))
    dec = np.degrees(np.array(decs))
    Es = np.array(E_list)
    mask = np.less(dec,-70)&np.greater(dec,-76)&np.less(ra, 152)&np.greater(ra, 145)
    logE = Es[mask]
    Ealpha = (logE-np.min(logE))/(np.max(logE)-np.min(logE))
    sc = plt.scatter(ra[mask],dec[mask], color='k',
                     c=logE, lw=0, cmap=cmaps['plasma'], s = 2**2)
    clb = plt.colorbar(sc, orientation='vertical')
    clb.set_label('logE', fontsize=20)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Zoomed region on hessj1507 with events',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--outFile', default='hotspot_zoom.pdf',
                   help='file name')
    p.add_argument("--xsize", type=int, default=1000,
                   help="Number of X pixels, Y will be scaled acordingly.")
    p.add_argument("--scale", type=float, default=1.,
                   help="scale up or down values in map")
    p.add_argument("--dmer", type=float, default=2.,
                   help="Interval in degrees between meridians.")
    p.add_argument("--dpar", type=float,default=1.,
                   help="Interval in degrees between parallels")
    args = p.parse_args()

    plot_events(args.prefix)

    dec = -73.4039433
    ra =  148.42541436
    plt.scatter(ra, dec, marker='+', color = 'green', s = 2**6)
    ax = plt.gca()
    ax.grid(color='k', alpha=0.2)
    ax.set_xlim([145,152])
    ax.set_ylim([-75,-70])

    ax.set_xlabel('RA [$^\circ$]')
    ax.set_ylabel('Dec [$^\circ$]')
    plt.savefig(fig_dir+args.outFile)
    plt.close()
