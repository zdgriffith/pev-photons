#!/usr/bin/env python

######################################
###  Plot a skymap projected with  ###
###  the South Pole at the center  ###
######################################

import argparse
import sys, sky
import healpy as hp
import numpy as np

from mpl_toolkits.basemap import Basemap

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib import cm
from support_functions import get_fig_dir
fig_dir = get_fig_dir()

#Custom color map in the style of Stefan's
ps_map = {'blue' : ((0.0, 0.0, 1.0),
                    #(0.05, 1.0, 1.0),
                    (0.17, 1.0, 1.0),
                    (0.4, 1.0, 1.0),
                    (0.6, 1.0, 1.0),
                    (0.7, 0.2, 0.2),
                    (1.0, 0.0, 0.0)),
          'green': ((0.0, 0.0, 1.0),
                    #(0.05, 1.0, 1.0),
                    (0.17, 1.0, 1.0),
                    (0.5, 0.0416, 0.0416),
                    (0.6, 0.0, 0.0),
                    (0.8, 0.5, 0.5),
                    (1.0, 1.0, 1.0)),
          'red':   ((0.0, 0.0, 1.0),
                   #(0.05, 1.0, 1.0),
                   (0.17, 1.0, 1.0),
                   (0.5, 0.0416, 0.0416),
                   (0.6, 0.0416, 0.0416),
                   (0.7, 1.0, 1.0),
                    (1.0, 1.0, 1.0))}

ps_map = LinearSegmentedColormap('ps_map', ps_map, 256)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/all_sky/',
                   help    = 'base directory for file storing')
    p.add_argument('--mapFile', dest='mapFile', type = str,
                   default = 'p_value_skymap.npy',
                   help    = 'file containing the skymap to plot')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'all_sky_scan.png',
                   help    = 'file name')
    p.add_argument('--noPlane', dest='noPlane', action = 'store_true',
            default = False, help='if True, do not draw galactic plane')
    p.add_argument('--noGrid', dest='noGrid', action = 'store_true',
            default = False, help='if True, do not draw grid lines')
    args = p.parse_args()

    filename = args.prefix+args.mapFile
    m        = np.load(filename)
    nside    = hp.npix2nside(len(m))
    npix     = hp.nside2npix(nside)
    DEC, RA  = hp.pix2ang(nside, range(len(m)))

    f=plt.figure(num=1, figsize=(12,8))
    f.clf()
    ax=f.add_subplot(1,1,1,axisbg='white')
 
    #South Pole Projection
    map1=Basemap(projection='spstere',boundinglat=-50,lon_0=0)

    #Draw Grid Lines
    if not args.noGrid:
        map1.drawmeridians(np.arange(0,360,15), linewidth=1, labels=[1,0,0,1], labelstyle='+/-',fontsize=16)
        map1.drawparallels(np.arange(-90,-45,5), linewidth=1, labels=[0,0,0,0], labelstyle='+/-',fontsize=16)

        #Draw Grid Labels
        x,y=map1(45,-80)
        plt.text(x,y,'-80$\degree$',fontsize=16)
        x,y=map1(45,-70)
        plt.text(x,y,'-70$\degree$',fontsize=16)
        x,y=map1(45,-60)
        plt.text(x,y,'-60$\degree$',fontsize=16)
        x,y=map1(45,-50)
        plt.text(x,y,'-50$\degree$',fontsize=16)

    #Draw Galactic Plane
    if not args.noPlane:
        tl=np.arange(-120,0,0.01)
        tb=np.zeros(np.size(tl))
        (tra,tdec)=sky.gal2eq(tl,tb)
        x,y=map1(tra,tdec)
        sc=map1.plot(x,y, 'k--',linewidth=1, label = 'Galactic Plane')

        tb=5*np.ones(np.size(tl))
        (tra,tdec)=sky.gal2eq(tl,tb)
        x,y=map1(tra,tdec)
        sc=map1.plot(x,y, 'k-',linewidth=1)

        tb=-5*np.ones(np.size(tl))
        (tra,tdec)=sky.gal2eq(tl,tb)
        x,y=map1(tra,tdec)
        sc=map1.plot(x,y, 'k-',linewidth=1)

    #Draw TS Map
    x,y=map1(np.degrees(RA), 90-np.degrees(DEC))
    sc=map1.scatter(x, y, c=-np.log10(m), vmin=0, vmax = 4.5, cmap=ps_map, s=2, lw=0, zorder=0)
    clb=f.colorbar(sc, orientation='vertical')
    clb.set_label('-log$_{10}$p', fontsize=20)
    
    #Label for unpublished plots
    x,y = map1(45,-37)
    plt.text(x,y, 'IceCube Preliminary', color = 'r', fontsize=14)

    #Hotspot in original result
    x,y=map1(214.7,-70.9)
    plt.scatter(x,y,edgecolor = 'g', marker = 'o', s = 2**7, lw = 1, facecolor = 'none')

    plt.legend()
    plt.savefig(fig_dir+args.outFile, facecolor = 'none', dpi=300, bbox_inches = 'tight') 
    plt.close()
