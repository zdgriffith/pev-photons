#!/usr/bin/env python

########################################################################
# Plot a rectangular box centered on galactic plane with HESS sources.
########################################################################

import argparse
import copy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

import healpy as hp

from pev_photons.utils.support import prefix, resource_dir
from pev_photons.utils.support import fig_dir, ps_map, plot_style

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
    
    nbottom = 0
    ntop = 0
    for src in sources:
        if src['plot']:
            if src['position'] == 'b':
                nbottom += 1
            if src['position'] == 't':
                ntop += 1
    
    def GetFractionalX(i,ntot,position):
        xmin2 = xmin
        xmax2 = xmax
        margin = 0.11 * (xmax-xmin)
        if position == 't':
            xmin2 += margin
        elif position == 'b':
            xmax2 -= margin
        else:
            sys.exit('Error: position must be "t" or "b", got',position)

        if i >= ntot:
            sys.exit('Error: "i >= ntot"')
        result = xmin2 + (i+0.5)*(xmax2-xmin2)/(ntot)
        return result
    
    ibottom = 0
    #itop = 0
    #itop = [3,0,2,1,4,5,6,7,8,9,10,11,12]
    itop = [3,0,2,1,4,5,6,7,8,10,9,11,12,13,14]
    
    for index, src in enumerate(sources):
        if src['plot']:
            ax.scatter(src['x'], src['y'], marker=src['marker'],
                       zorder=src['zorder'],
                       color='none',
                       facecolors=src['color'],
                       alpha=src['alpha'],
                       s=src['markersize'])

            if 'plotLabel' in src and src['plotLabel']:
                angle = src['angle']
                ddec = 0.003
                dra = 0
                if angle >= 0 and angle < 180:
                    verticalalignment = 'bottom'
                    horizontalalignment = 'left'
                    if src['position'] == 'h':
                        dra = -0.03
                else:
                    verticalalignment = 'top'
                    horizontalalignment = 'right'
                    angle += 180
                    ddec = -ddec
                    if src['position'] == 'h':
                        dra = 0.03
                s = str(src['name'])
                xx = src['x']+dra*(xmax-xmin)
                yy = src['y']+ddec*(ymax-ymin)
            
                # Draw a line between pointLabel and pointSource
                # Keep a little distance to the source.
                def DrawLine(pl,ps,ax,toskip=0.015*(ymax-ymin)):
                    linelength = np.sqrt(np.power(ps[1]-pl[1],2) +
                                         np.power(
                                           np.cos(np.deg2rad((ps[0]-pl[0])/2.))*
                                           (ps[0]-pl[0]),2))
                    # print 'linelength', linelength, 'toskip', toskip
                    ps2 = copy.deepcopy(ps)
                    for i in [0,1]:
                        ps2[i] = pl[i] + (1-toskip/linelength) * (ps[i]-pl[i])
                    ax.plot([ps2[0],pl[0]], [ps2[1],pl[1]], 'w-', linewidth=2.0)
                    ax.plot([ps2[0],pl[0]], [ps2[1],pl[1]], 'k-', linewidth=1.0)
                offset = 0.
                # offset = 0.05 * (xmax-xmin)
                if src['position'] == 'b':
                    xx = GetFractionalX(ibottom,nbottom,src['position'])
                    yy = ymin + 0.25 * (ymax-ymin)
                    ibottom += 1
                    DrawLine([xx - offset, yy], [src['x'], src['y']], ax)
                    horizontalalignment = 'right'
                if src['position'] == 't':
                    xx = GetFractionalX(itop[index],ntop,src['position'])
                    yy = ymin + 0.75 * (ymax-ymin)
                    #itop += 1
                    DrawLine([xx + offset, yy], [src['x'], src['y']], ax)
                    horizontalalignment = 'left'
                ax.text(xx,yy, s.replace("~"," "),
                        color=src['color'],
                        rotation=angle,
                        verticalalignment=verticalalignment, # center top bottom baseline
                        horizontalalignment=horizontalalignment, # center right left
                        fontdict={'family': 'sans-serif',
                                  'size': src['size'],
                                  'weight': 'bold'},
                        path_effects=[pe.withStroke(linewidth=5,
                                                    foreground=src['bkgcolor'],
                                                    alpha=src['alpha']
                                                   )
                                     ]
                       )

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Rectangular Projection of the HESS source region',
            formatter_class=argparse.RawDescriptionHelpFormatter)
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

    plt.style.use(plot_style)

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
    
    # Read in the skymap and mask out empty pixels
    skymap = np.load(prefix+args.mapFile)
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
    figsize = (fysize*faspect+2, fysize+2.75)
    fig = plt.figure(num=1,figsize=figsize)
    
    tfig = plt.figure(num=2,figsize=figsize)
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

    f = np.load(resource_dir+'hess_sources.npz')
    sources = []
    for i, name in enumerate(f['name']):
        print(name)
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
    print(yts)

    imgp = ax.imshow(rotimg,extent=[cxmax, cxmin, ymax,ymin],\
                     vmin=0,vmax=4.5,cmap=ps_map)
    ax.grid(color='k', alpha=0.2)
    ax.xaxis.set_ticks(xts)
    ax.xaxis.set_ticklabels(xtlbs)
    ax.yaxis.set_ticks(yts)
    ax.set_xlabel('l [$^\circ$]')
    ax.set_ylabel('b [$^\circ$]')
    ax.text(-30.5, -4.75, 'IceCube Preliminary', color='r', fontsize=14, zorder=5)
    plt.gca().invert_yaxis()
    plt.savefig(fig_dir+'TeVCat/HESS_srcs_w_labels.pdf')
    plt.savefig(fig_dir+'paper/hess_sources.pdf')
    plt.close()
