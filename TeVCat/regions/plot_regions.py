#!/usr/bin/env python

########################################################################
# Plot a box zoomed in, centered on a source position in galactic coords.
########################################################################

import argparse
import sys
import copy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

import healpy as hp
from support_functions import get_fig_dir

from map_w_srcs import ps_map

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()

def PlotSources(sources, coords, ax, frot, xmin, xmax, ymin, ymax):

    cRot = hp.Rotator(coord=["C",coords[-1]])
    for src in sources:
        y,x = cRot(np.pi*0.5 - np.deg2rad(src['Dec']), np.deg2rad(src['RA']))
        x = np.rad2deg(x) + frot
        if x>180.:
            x -= 360.
        y = 90. - np.rad2deg(y)
        plot = (x > xmin) & (x < xmax) & (y > ymin) & (y < ymax)
        src['x'] = x
        src['y'] = y
        src['plot'] = plot
    
    sources.sort(key=lambda x: x['x'])
    
    for index, src in enumerate(sources):
        if src['plot']:
            ax.scatter(src['x'], src['y'], marker=src['marker'],
                       zorder=src['zorder'],
                       color='none',
                       facecolors=src['color'],
                       alpha=src['alpha'],
                       s=src['markersize'])

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Box around a source location',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--mapFile',
                   default='all_sky/p_value_skymap.npy',
                   help='file containing the skymap to plot')
    p.add_argument("--xsize", type=int, default=1000,
                   help="Number of X pixels, Y will be scaled acordingly.")
    p.add_argument("--scale", type=float, default=1.,
                   help="scale up or down values in map")
    p.add_argument("--catLabelsAngle", type=float,
                   default=30., help="Oriantation of catalog labels.")
    p.add_argument("--catLabelsSize", type=float,
                   default=12., help="Size of catalog labels.")
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

    xmin, xmax, ymin, ymax = [330,282,-5,5]
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
    
    f = np.load(args.prefix+'TeVCat/hess_sources.npz')

    for j, dec in enumerate(f['dec']):
        print(j)
        outFile = 'source_%s_extended.pdf' % j
        cRot = hp.Rotator(coord=["C","G"])
        y,x = cRot(np.pi*0.5 - np.deg2rad(dec), np.deg2rad(f['ra'][j]))
        x = np.rad2deg(x) + frot
        if x>180.:
            x -= 360.
        y = 90. - np.rad2deg(y)

        # Read in the skymap and mask out empty pixels
        skymap = np.load(args.prefix+'TeVCat/source_regions/source_%s_extended_p_value.npy' % j)
        # remove naughty values
        skymap[np.isnan(skymap)] = hp.UNSEEN
        skymap *= args.scale
        nside1 = hp.get_nside(skymap)
        npix = hp.nside2npix(nside1)

        # Set up the figure frame and coordinate rotation angle
        coords = ["C","G"]
        gratcoord = "G"

        faspect = abs(cxmax - cxmin)/abs(ymax-ymin)
        fysize = 4
        figsize = (fysize, fysize)
        #fig = plt.figure(num=1,figsize=figsize)
        fig = plt.figure(num=1)
        
        #tfig = plt.figure(num=2,figsize=figsize)
        tfig = plt.figure(num=2)
        rotimg = hp.cartview(-np.log10(skymap), fig=2, coord=coords, title="",\
                             cmap=ps_map, cbar=False,\
                             lonra=[cxmin,cxmax], latra=[ymin,ymax], #rot=rotMap,
                             notext=True, xsize=args.xsize,
                             return_projected_map=True)
        plt.close(tfig)

        #TeVCat sources
        ax = fig.add_subplot(111)
        ax.set_aspect(1.)

        defaultsource = {'marker': 'o',
                         'markersize': 35.,
                         'zorder': 2,
                         'color': 'k',
                         'bkgcolor': 'w',
                         'alpha': 1.,
                         'size': args.catLabelsSize,
                         'angle': args.catLabelsAngle,
                         'position': 't', # h(ere), t(op), b(ottom)
                         'plotLabel': True
                        }

        sources = []
        for i, name in enumerate(f['name']):
            #if i == 0 or i >2:
            src = copy.deepcopy(defaultsource)
            src['RA'] = f['ra'][i]
            src['Dec'] = f['dec'][i]
            src['name'] = name
            sources.append(src)
            
        PlotSources(sources, coords, ax, frot, xmin, xmax, ymin, ymax)

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
                if args.isMoon or args.isSun:
                    cval -= 180.
                    if cval < -180.:
                        cval+=360.
                elif args.coords=='C' and cval<0:
                    cval+=360
                
                xtlbs.append('%g'%(cval))
        yts = np.arange(np.floor(ymin), np.ceil(ymax+args.dpar), args.dpar)[1:-1]

        imgp = ax.imshow(rotimg,extent=[cxmax, cxmin, ymax,ymin],\
                         vmin=0,vmax=4.5,cmap=ps_map)
        ax.grid(color='k', alpha=0.2)
        ax.xaxis.set_ticks(xts)
        ax.xaxis.set_ticklabels(xtlbs)
        ax.yaxis.set_ticks(yts)
        ax.set_xlim([x-2,x+2])
        ax.set_ylim([y-2,y+2])
        ax.set_xlabel('l [$^\circ$]')
        ax.set_ylabel('b [$^\circ$]')
        plt.gca().invert_yaxis()
        plt.savefig(fig_dir+outFile)
        plt.close()
