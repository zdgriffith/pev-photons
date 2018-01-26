#!/usr/bin/env python

########################################################################
# Plot a skymap projected with the South Pole at the center.
########################################################################

import argparse
import matplotlib.pyplot as plt
import numpy as np

from utils.support import prefix, plot_style, fig_dir, ps_map
from utils.skymap import PolarSkyMap

if __name__ == "__main__":
    p = argparse.ArgumentParser(
                   description='Plot a skymap with a south polar projection.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--extension', type=float, default=0,
                   help='Spatial extension to source hypothesis in degrees.')
    p.add_argument('--noPlane', action='store_true', default=False,
                   help='If True, do not draw galactic plane.')
    p.add_argument('--noGrid', action='store_true', default=False,
                   help='If True, do not draw grid lines.')
    p.add_argument('--HESE', action='store_true', default=False,
                   help='If True, plot the HESE cascades.')
    args = p.parse_args()

    plt.style.use(plot_style)

    if args.extension:
        inFile = prefix + 'all_sky/ext/p_value_skymap_ext_%s.npy' % args.extension
        outFile = 'all_sky_scan_ext_%s.pdf' % args.extension
    else:
        inFile = prefix + 'all_sky/p_value_skymap.npy'
        outFile = 'all_sky_scan.pdf'

    fig, ax = plt.subplots(figsize=(12,8))

    skymap = PolarSkyMap(fig, ax)
 
    if not args.noGrid:
        skymap.plot_grid()

    if not args.noPlane:
        skymap.plot_galactic_plane()

    # Plot the pre-trial p-value as -log_10(p-value)
    healpy_map = -np.log10(np.load(inFile))
    scatter_args = {'cmap':ps_map, 's':2, 'lw':0, 'zorder':0,
                    'vmin':0, 'vmax':4.5, 'rasterized':True}

    skymap.plot_sky_map(healpy_map, colorbar_label='-log$_{10}$p',
                        **scatter_args)
    
    if args.HESE:
        # plot the HESE cascade events and their 1 sigma errors
        skymap.plot_HESE()
    else:
        # Hightlights the hotspot of the skymap
        dec = -73.4039433
        ra =  148.42541436
        x, y = skymap.basemap(ra, dec)
        plt.scatter(x, y, marker='o', s=2**9, lw=2,
                    edgecolor='g', facecolor='none')

    ax.legend()
    plt.savefig(fig_dir+'all_sky/'+outFile)
    if args.HESE:
        plt.savefig(fig_dir+'paper/hese_events.pdf')
    elif not args.extension:
        plt.savefig(fig_dir+'paper/all_sky_scan.pdf')
    plt.close()
