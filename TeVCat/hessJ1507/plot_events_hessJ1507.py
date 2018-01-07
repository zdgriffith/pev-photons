#!/usr/bin/env python

########################################################################
# Zoomed Region on hessJ1507 with events
########################################################################

import argparse
import copy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

import healpy as hp
from support_functions import get_fig_dir

from map_w_srcs import ps_map
from matplotlib import cm

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()
from colormaps import cmaps

def plot_events(pf, frot):
    years = ['2011', '2012', '2013', '2014','2015']
    decs = []
    ras = []
    E_list = []
    for i, year in enumerate(years): 
        exp = np.load(pf+'/datasets/'+year+'_exp_ps.npy')
        decs.extend(exp['dec'])
        ras.extend(exp['ra'])
        E_list.extend(exp['logE'])
        
    ra = np.array(ras)
    dec = np.array(decs)
    Es = np.array(E_list)
    cRot = hp.Rotator(coord=["C",coords[-1]])
    y,x = cRot(np.pi*0.5 - dec, ra)
    x = np.rad2deg(x) + frot
    for i, x_i in enumerate(x):
        if x_i>180.:
            x[i] -= 360.
    y = 90. - np.rad2deg(y)
    mask = np.less(y,-1)&np.greater(y,-6)
    logE = Es[mask]
    Ealpha = (logE-np.min(logE))/(np.max(logE)-np.min(logE))
    sc = plt.scatter(x[mask],y[mask], color='k',
                     c=logE, lw=0, cmap=cmaps['plasma'])
    clb = plt.colorbar(sc, orientation='vertical')
    clb.set_label('logE', fontsize=20)

def plot_contour(pf, frot, ax):
    cRot = hp.Rotator(coord=["C",coords[-1]])
    a = np.loadtxt(pf+'/TeVCat/hessJ1507_contour.txt')
    ra, dec = a.T
    y,x = cRot(np.pi*0.5 - np.deg2rad(dec), np.deg2rad(ra))
    x = np.rad2deg(x) + frot
    for i, x_i in enumerate(x):
        if x_i>180.:
            x[i] -= 360.
    y = 90. - np.rad2deg(y)
    ax.plot(x,y, color = 'k', zorder = 10)

def plot_hotspot(ax):
    circle = plt.Circle((-42.65, -3.42), 0.4, color='k', lw = 1, fill=False)
    ax.add_artist(circle)

def plot_skymap(args, ax):
    skymap = np.load(args.prefix+args.mapFile)
    rotimg = hp.cartview(-np.log10(skymap), fig=2, title="",\
                         cmap=cm.gist_rainbow_r, cbar=False,\
                         lonra=[cxmin,cxmax], latra=[ymin,ymax], #rot=rotMap,
                         notext=True, xsize=args.xsize,
                         return_projected_map=True)
    imgp = ax.imshow(rotimg,extent=[cxmax, cxmin, ymax,ymin],\
                     vmin=-2,vmax=14, zorder = -2,
                     cmap=cm.gist_rainbow_r)

    return ax
if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Zoomed region on hessj1507 with events',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--mapFile',
                   default='galactic_plane/co_hp_map.npy',
                   help='file containing the skymap to plot')
    p.add_argument('--outFile', default='HESSJ1507_zoom.pdf',
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

    # Fill 2D array
    xmin = -180.
    xmax = 180.
    ymax = 90
    ymin = -90

    xmin, xmax, ymin, ymax = [320,314,-5.5,-1.5]
    xC = (xmin+xmax) / 2.
    yC = (ymin+ymax) / 2.

    # Move to range expected by healpy
    while xmin < -180:
        xmin += 360
    while xmin > 180:
        xmin -= 360
    while xmax < -180:
        xmax += 360
    while xmax > 180:
        xmax -= 360

    if xmax < xmin:
        tmax = xmax
        tmin = xmin
        xmin = tmax
        xmax = tmin

    cxmin = xmin
    cxmax = xmax
    frot =0.
    if xmax > 90. and xmin < -90.:
      frot = 180.
      cxmin = xmax - 180.
      cxmax = xmin + 180.
    
    # Set up the figure frame and coordinate rotation angle
    coords = ["C","G"]
    gratcoord = "G"

    faspect = abs(cxmax - cxmin)/abs(ymax-ymin)
    fysize = 4
    fig = plt.figure(num=1)
    
    # Draw grid lines
    xts = np.arange(np.floor(xmin), np.ceil(xmax+args.dmer), args.dmer)[1:-1]
    xtlbs = ['%g'%xt for xt in xts]
    if xmin < 0. and xmax > 0. and (xmax-xmin) > 180.:
        xts = np.arange(np.floor(cxmin), np.ceil(cxmax+args.dmer), args.dmer)[1:-1]
        xtlbs = [   ]
        for xt in xts:
            cval = xt - 180.
            if xt < 0:
                cval = 180.+xt
            if cval == -180:
                cval = 180
            elif args.coords=='C' and cval<0:
                cval+=360
            
            xtlbs.append('%g'%(cval))
    yts = np.arange(np.floor(ymin), np.ceil(ymax+args.dpar), args.dpar)[1:-1]

    ax = plt.gca()
    plot_events(args.prefix, frot)
    #plot_skymap(args, ax)
    plot_contour(args.prefix, frot, ax)
    plot_hotspot(ax)

    ax.grid(color='k', alpha=0.2)
    ax.xaxis.set_ticks(xts)
    ax.xaxis.set_ticklabels(xtlbs)
    ax.yaxis.set_ticks(yts)
    ax.set_xlim([-41,-44])
    ax.set_ylim([-1.5,-5.5])
    ax.set_xlabel('l [$^\circ$]')
    ax.set_ylabel('b [$^\circ$]')
    plt.gca().invert_yaxis()
    plt.savefig(fig_dir+args.outFile)
    plt.close()
