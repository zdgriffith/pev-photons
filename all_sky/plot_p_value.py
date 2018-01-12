#!/usr/bin/env python

########################################################################
# Plot a skymap projected with the South Pole at the center.
########################################################################

import argparse
import healpy as hp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib import cm

from mpl_toolkits.basemap import Basemap

from pev_photons.support import prefix, plot_style, fig_dir, ps_map

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
    args = p.parse_args()

    plt.style.use(plot_style)

    if args.extension:
        inFile = prefix + 'all_sky/ext/p_value_skymap_ext_%s.npy' % args.extension
        outFile = 'all_sky_scan_ext_%s.pdf' % args.extension
    else:
        inFile = prefix + 'all_sky/p_value_skymap.npy'
        outFile = 'all_sky_scan.pdf'

    m = np.load(inFile)
    nside = hp.npix2nside(len(m))
    npix  = hp.nside2npix(nside)
    DEC, RA = hp.pix2ang(nside, range(len(m)))

    f = plt.figure(num=1, figsize=(12,8))
    f.clf()
    ax=f.add_subplot(1,1,1,axisbg='white')
 
    # Define projection to be from the South Pole.
    map1=Basemap(projection='spstere',boundinglat=-50,lon_0=0)

    # Draw the grid lines and labels.
    if not args.noGrid:
        map1.drawmeridians(np.arange(0,360,15), linewidth=1,
                           labels=[1,0,0,1], labelstyle='+/-',
                           fontsize=16)
        map1.drawparallels(np.arange(-90,-45,5), linewidth=1,
                           labels=[0,0,0,0], labelstyle='+/-',
                           fontsize=16)

        x,y = map1(45,-80)
        plt.text(x, y, '-80$^{\circ}$', fontsize=16)
        x,y = map1(45,-70)
        plt.text(x, y, '-70$^{\circ}$', fontsize=16)
        x,y = map1(45,-60)
        plt.text(x, y, '-60$^{\circ}$', fontsize=16)
        x,y = map1(45,-50)
        plt.text(x, y, '-50$^{\circ}$', fontsize=16)

    # Draw the galactic plane.
    if not args.noPlane:
        cRot = hp.Rotator(coord = ['G','C'], rot = [0, 0])
        tl = np.radians(np.arange(0,360, 0.01))
        tb = np.radians(np.full(tl.size, 90))
        tdec, tra = np.degrees(cRot(tb,tl))
        x,y = map1(tra, 90-tdec)
        sc  = map1.plot(x, y, 'k--', linewidth=1, label='Galactic Plane')

        tb = np.radians(np.full(tl.size, 95))
        tdec, tra = np.degrees(cRot(tb,tl))
        x,y = map1(tra, 90-tdec)
        sc  = map1.plot(x, y, 'k-', linewidth=1)

        tb = np.radians(np.full(tl.size, 85))
        tdec, tra = np.degrees(cRot(tb,tl))
        x,y = map1(tra, 90-tdec)
        sc  = map1.plot(x, y, 'k-', linewidth=1)

    # Draw the test statistic map.
    x,y = map1(np.degrees(RA), 90-np.degrees(DEC))
    sc  = map1.scatter(x, y,
                       c=-np.log10(m),
                       vmin=0, vmax=4.5,
                       cmap=ps_map,
                       s=2, lw=0, zorder=0, rasterized=True)
    clb = f.colorbar(sc, orientation='vertical')
    clb.set_label('-log$_{10}$p', fontsize=20)
    
    # Draw a label for unpublished plots.
    x,y = map1(45, -37)
    plt.text(x, y, 'IceCube Preliminary',
             color='r', fontsize=14)

    # Hightlights the hotspot of the skymap
    dec = -73.4039433
    ra =  148.42541436
    x,y = map1(ra, dec)
    plt.scatter(x, y, marker='o', s=2**8, lw=1,
                edgecolor='g', facecolor='none')
    plt.legend()
    plt.savefig(fig_dir+'all_sky/'+outFile)
    if not args.extension:
        plt.savefig(fig_dir+'paper/all_sky_scan.pdf')
    plt.close()
