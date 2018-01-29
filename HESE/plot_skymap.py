#!/usr/bin/env python

########################################################################
# Plot a skymap projected with the South Pole at the center.
########################################################################

import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

import healpy as hp

from utils.support import prefix, plot_style, fig_dir, plasma_map
from utils.skymap import PolarSkyMap

if __name__ == "__main__":
    p = argparse.ArgumentParser(
                   description='Plot a skymap with a south polar projection.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--mapName', type = str,
                   default='cascades',
                   help='Name of the skymap to plot.')
    p.add_argument('--noPlane', action='store_true', default=False,
                   help='If True, do not draw galactic plane.')
    p.add_argument('--noGrid', action='store_true', default=False,
                   help='If True, do not draw grid lines.')
    args = p.parse_args()

    plt.style.use(plot_style)

    fig, ax = plt.subplots(figsize=(12,8))

    skymap = PolarSkyMap(fig, ax)
 
    if not args.noGrid:
        skymap.plot_grid()

    if not args.noPlane:
        skymap.plot_galactic_plane()

    filename = prefix+'/HESE/2011/'+args.mapName+'_exp.npy'
    hmap = np.load(filename)
    hmap = hp.ud_grade(hmap.item()['signal_x_acceptance_map'], nside_out=512)
    hmap = len(hmap)*hmap/np.sum(hmap[np.isfinite(hmap)])
    scatter_args = {'cmap':plasma_map,
                    'norm':LogNorm(vmin=5*10**-2, vmax=np.max(hmap)),
                    's':2**3, 'lw':0, 'zorder':0, 'rasterized':True}

    skymap.plot_sky_map(hmap, colorbar_label='[A.U.]',
                        **scatter_args)
    
    ax.legend()
    plt.savefig(fig_dir+'HESE/'+args.mapName+'_x_acc.pdf',
                bbox_inches='tight')
    plt.close()
