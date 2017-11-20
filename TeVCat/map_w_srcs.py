#!/usr/bin/env python

########################################################################
# Plot a skymap projected to a rectangular view of the HESS source region               
########################################################################

import argparse, math
import sky
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.basemap import Basemap
import healpy as hp
from optparse import OptionParser
from matplotlib.colors import LinearSegmentedColormap
from support_functions import get_fig_dir
fig_dir = get_fig_dir()
plt.style.use('mystyle')
colors = mpl.rcParams['axes.color_cycle']

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

def polar_stere(lon_w, lon_e, lat_s, lat_n, **kwargs):
    '''Returns a Basemap object (NPS/SPS) focused in a region.
    source: http://code.activestate.com/recipes/578379-plotting-maps-with-polar-stereographic-projection-/

    lon_w, lon_e, lat_s, lat_n -- Graphic limits in geographical coordinates.
                                  W and S directions are negative.
    **kwargs -- Aditional arguments for Basemap object.
    '''

    lon_0 = lon_w + (lon_e - lon_w) / 2.
    ref = lat_s if abs(lat_s) > abs(lat_n) else lat_n
    lat_0 = math.copysign(90., ref)
    proj = 'npstere' if lat_0 > 0 else 'spstere'
    prj = Basemap(projection=proj, lon_0=lon_0, lat_0=lat_0,
                          boundinglat=0)
    lons = [lon_w, lon_e, lon_w, lon_e, lon_0, lon_0]
    lats = [lat_s, lat_s, lat_n, lat_n, lat_s, lat_n]
    x, y = prj(lons, lats)
    ll_lon, ll_lat = prj(min(x), min(y), inverse=True)
    ur_lon, ur_lat = prj(max(x), max(y), inverse=True)
    return Basemap(projection='stere', lat_0=lat_0, lon_0=lon_0,
                           llcrnrlon=ll_lon, llcrnrlat=ll_lat,
                           urcrnrlon=ur_lon, urcrnrlat=ur_lat, **kwargs)

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Rectangular Projection of the HESS source region',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--mapFile', dest='mapFile', type = str,
                   default = 'all_sky/p_value_skymap.npy',
                   help    = 'file containing the skymap to plot')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'scan_in_HESS_region.png',
                   help    = 'file name')
    p.add_argument('--noPlane', dest='noPlane', action = 'store_true',
            default = False, help='if True, do not draw galactic plane')
    p.add_argument('--noGrid', dest='noGrid', action = 'store_true',
            default = False, help='if True, do not draw grid lines')
    args = p.parse_args()

    ratio   = 1.25
    figure  = plt.figure(figsize=(ratio*8,ratio*4))
    m       = np.load(args.prefix+args.mapFile)
    nside   = hp.npix2nside(len(m))
    npix    = hp.nside2npix(nside)
    DEC, RA = hp.pix2ang(nside, range(len(m)))

    map1 = polar_stere(-30,60,-70,-55) 

    #Draw Grid Lines
    if not args.noGrid:
        map1.drawmeridians(np.arange(0,360,15), linewidth=1, labels=[0,0,0,0], labelstyle='+/-',fontsize=16)
        map1.drawparallels(np.arange(-90,-45,5), linewidth=1, labels=[0,0,0,0], labelstyle='+/-',fontsize=16)
        x,y=map1(-48,-58)
        plt.text(x,y,'135$\degree$',fontsize=16)
        x,y=map1(-35,-53)
        plt.text(x,y,'150$\degree$',fontsize=16)
        x,y=map1(-15,-49.8)
        plt.text(x,y,'165$\degree$',fontsize=16)
        x,y=map1(0,-53.65)
        plt.text(x,y,'180$\degree$',fontsize=16)
        x,y=map1(15,-54.85)
        plt.text(x,y,'195$\degree$',fontsize=16)
        x,y=map1(30,-53.65)
        plt.text(x,y,'210$\degree$',fontsize=16)
        x,y=map1(45,-49.8)
        plt.text(x,y,'225$\degree$',fontsize=16)
        x,y=map1(15,-70)
        plt.text(x,y,'-70$\degree$',fontsize=16)
        x,y=map1(15,-60)
        plt.text(x,y,'-60$\degree$',fontsize=16)

    #Draw Galactic Plane
    if not args.noPlane:
        tl=np.arange(-120,0,0.01)
        tb=np.zeros(np.size(tl))
        (tra,tdec)=sky.gal2eq(tl,tb)
        x,y=map1(180+tra,tdec)
        sc=map1.plot(x,y, 'k--',linewidth=1, label = 'Galactic Plane')
        tl=np.arange(-120,0,0.01)
        tb=5*np.ones(np.size(tl))
        (tra,tdec)=sky.gal2eq(tl,tb)
        x,y=map1(180+tra,tdec)
        sc=map1.plot(x,y, 'k-',linewidth=1)
        tl=np.arange(-120,0,0.01)
        tb=-5*np.ones(np.size(tl))
        (tra,tdec)=sky.gal2eq(tl,tb)
        x,y=map1(180+tra,tdec)
        sc=map1.plot(x,y, 'k-',linewidth=1)

    #Load HESS Sources
    f    = np.load(args.prefix+'TeVCat/hess_sources.npz')
    print(f['name'])
    ras  = np.append(f['ra'][0], f['ra'][3:])
    decs = np.append(f['dec'][0], f['dec'][3:])
    sc   = map1.scatter(180+ras, decs, latlon=True, marker = 'x',
                        lw = 1.25, color = 'forestgreen', zorder = 10,
                        s = 2**5, label = 'H.E.S.S. Sources')

    #Draw TS Map
    x,y = map1(180+np.degrees(RA), 90-np.degrees(DEC))
    sc  = map1.scatter(x, y, c=-np.log10(m), vmin=0, vmax = 4.5, cmap=ps_map, s=2**2, lw=0, zorder=0)
    clb = plt.colorbar(sc, orientation='horizontal',fraction=0.046, pad=0.04)
    clb.ax.tick_params(labelsize=12)
    clb.set_label('-log$_{10}$p', fontsize=20)

    x,y = map1(-44,-62)
    plt.text(x,y, 'IceCube Preliminary', color = 'r', fontsize=14)

    plt.legend(loc = 'lower right', fontsize =10)
    plt.savefig(fig_dir+args.outFile, facecolor = 'none', dpi=300, bbox_inches = 'tight') 
    plt.close()
