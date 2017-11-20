#!/usr/bin/env python

########################################################################
# Plot of the CO map from Dame (2001) around HESS J1507
########################################################################

import numpy as np
import matplotlib.pyplot as plt
import healpy as hp

from support_functions import get_fig_dir
plt.style.use('stefan')
fig_dir = get_fig_dir()
import matplotlib as mpl
colors = mpl.rcParams['axes.color_cycle']
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib import cm

def extents(f):
  delta = f[1] - f[0]
  return [f[0] - delta/2, f[-1] + delta/2]

def plot_contour():
    frot = 180.
    cRot = hp.Rotator(coord=["C","G"])
    a = np.loadtxt('/data/user/zgriffith/pev_photons/TeVCat/hessJ1507_contour.txt')
    ra, dec = a.T
    y,x = cRot(np.pi*0.5 - np.deg2rad(dec), np.deg2rad(ra))
    x = np.rad2deg(x) + frot
    for i, x_i in enumerate(x):
        if x_i>180.:
            x[i] -= 360.
    y = 90. - np.rad2deg(y)
    plt.plot(180+x,y, color = 'k')

def plot_hotspot():
    ax = plt.gca()
    circle = plt.Circle((360-42.65, -3.42), 0.4, color='k', lw = 1, fill=False)
    ax.add_artist(circle)

if __name__ == "__main__":

    m = np.load('/data/user/zgriffith/pev_photons/galactic_plane/co_map_slice.npy')
   
    lat = np.linspace(-8.5, 23, 63)
    #lon = np.linspace(15, -150.5, 331)
    lon = np.linspace(375, 360-150.5, 331)

    sc = plt.imshow(m, aspect='auto', interpolation='none',
                    vmin=-2, vmax=14,
                    cmap = cm.gist_rainbow_r,
                    extent=extents(lon) + extents(lat), origin='lower')
    clb = plt.colorbar(sc, orientation='vertical')
    #clb.set_label('-log$_{10}$W', fontsize=20)
    clb.set_label('K', fontsize=20)

    plot_hotspot()
    plot_contour()

    #plt.xlim([-40,-46])
    plt.xlim([323,313])
    plt.ylim([-7,-1])
    plt.savefig(fig_dir+'co_test.pdf')
    plt.close()
