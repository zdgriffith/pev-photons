#!/usr/bin/env python

########################################################################
# Convert CO map from Dame (2001) around HESS J1507 to healpix map
########################################################################

import numpy as np
import matplotlib.pyplot as plt
import healpy as hp
import scipy

from support_functions import get_fig_dir
plt.style.use('stefan')
fig_dir = get_fig_dir()
import matplotlib as mpl
colors = mpl.rcParams['axes.color_cycle']
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib import cm

if __name__ == "__main__":

    m = np.load('/data/user/zgriffith/pev_photons/galactic_plane/co_map_slice.npy')
    lon = np.linspace(375, 360-150.5, 331)
    lat = np.linspace(-8.5, 23, 63)

    fine_lon = np.linspace(375, 360-150.5, 1000)
    fine_lat = np.linspace(-8.5, 23, 1000)

    x_mask = np.greater(fine_lat, -7)&np.less(fine_lat,-2)
    y_mask = np.greater(fine_lon, 314)&np.less(fine_lon, 320)
    x_index = np.argmin(np.abs(lat- fine_lat[:,np.newaxis]), axis = 1)[x_mask]
    y_index = np.argmin(np.abs(lon- fine_lon[:,np.newaxis]), axis = 1)[y_mask]

    nside = 128
    npix = hp.nside2npix(nside)
    hp_map = np.zeros(npix)
    gal_theta = np.pi/2. - np.radians(fine_lat)
    for i, x in enumerate(gal_theta[x_mask]):
        for j, y in enumerate(np.radians(fine_lon[y_mask])):
            if y >= 2*np.pi:
                y -= 2*np.pi
                
            p = hp.ang2pix(nside, x, y)
            hp_map[p] = m[x_index[i]][y_index[j]]

    np.save('/data/user/zgriffith/pev_photons/galactic_plane/co_hp_map.npy', hp_map)
    hp_map += np.abs(np.min(hp_map))
    #hp_map /= np.sum(hp_map)
    np.save('/data/user/zgriffith/pev_photons/galactic_plane/source_templates/co_map.npy', hp_map)
