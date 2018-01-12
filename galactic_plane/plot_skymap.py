#!/usr/bin/env python

########################################################################
# Plot a skymap projected with the South Pole at the center.
########################################################################

import argparse
import healpy as hp
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib import cm

from mpl_toolkits.basemap import Basemap
from pev_photons.support import prefix, plot_style, fig_dir, plasma_map

if __name__ == "__main__":
    p = argparse.ArgumentParser(
                   description='Plot a skymap with a south polar projection.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--mapName', type = str,
                   default='fermi_pi0',
                   help='Name of the skymap to plot.')
    p.add_argument('--noPlane', action='store_true', default=False,
                   help='If True, do not draw galactic plane.')
    p.add_argument('--noGrid', action='store_true', default=False,
                   help='If True, do not draw grid lines.')
    args = p.parse_args()

    plt.style.use(plot_style)

    filename = prefix+'/galactic_plane/2012/'+args.mapName+'_exp.npy'
    m = np.load(filename)
    m = m.item()['signal_x_acceptance_map']
    m = hp.ud_grade(m,nside_out=512)
    nside = hp.npix2nside(len(m))
    npix  = hp.nside2npix(nside)
    DEC, RA = hp.pix2ang(nside, range(len(m)))

    #Conversion from galactic coords if needed
    cRot = hp.Rotator(coord = ['G','C'], rot = [0, 0])
    DEC, RA = cRot(DEC, RA)

    #f = plt.figure(num=1, figsize=(12,8))
    f = plt.figure(num=1, figsize=(12,8))
    #f = plt.figure(num=1)
    f.clf()
    ax=f.add_subplot(1,1,1,axisbg='white')
 
    # Define projection to be from the South Pole.
    map1=Basemap(projection='spstere',boundinglat=-50,lon_0=0)

    # Draw the grid lines and labels.
    print(max(m))
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

    # Draw the map.
    m_norm = len(m)*m/np.sum(m[np.isfinite(m)]),
    x,y = map1(np.degrees(RA), 90-np.degrees(DEC))
    sc  = map1.scatter(x, y, c=m_norm, cmap=plasma_map,
                       norm=LogNorm(vmin=5*10**-2, vmax = np.max(m_norm)),
                       s=2**3, lw=0, zorder=0, rasterized=True)

    clb = f.colorbar(sc, orientation='vertical')
    clb.set_label('Magnitude [A.U.]')
    
    plt.legend()
    plt.savefig(fig_dir+'galactic_plane/'+args.mapName+'_x_acc.png',
                facecolor='none', dpi=300,
                bbox_inches='tight') 
    if args.mapName == 'fermi_pi0':
        plt.savefig(fig_dir+'paper/fermi_pi0_x_acc.pdf', bbox_inches='tight')
    plt.close()
