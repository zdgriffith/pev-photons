#!/usr/bin/env python

########################################################################
# Class for plotting skymaps using Basemap projected from the Pole
########################################################################

import numpy as np
from mpl_toolkits.basemap import Basemap

import healpy as hp

class PolarSkyMap(object):
    """ Class for plotting sky maps using Basemap projected from the Pole.

    Parameters
    ----------
    figure : matplotlib.figure.Figure
        matplotlib figure instance
    axes : matplotlib.axes._subplots.AxesSubplot
        matplotlib axes instance

    Attributes
    ----------
    basemap : mpl_toolkits.basemap.Basemap
        Basemap instance set to a South Pole Projection

    """

    def __init__(self, figure, axes):
        self.fig = figure
        self.ax = axes

        # Define projection to be from the South Pole.
        self.basemap = Basemap(projection='spstere',
                               boundinglat=-50, lon_0=0)


    def plot_grid(self):
        """ Plot grid lines. """

        self.basemap.drawmeridians(np.arange(0,360,15), linewidth=1,
                                   labels=[1,0,0,1], labelstyle='+/-',
                                   fontsize=16)
        self.basemap.drawparallels(np.arange(-90,-45,5), linewidth=1,
                                   labels=[0,0,0,0], labelstyle='+/-',
                                   fontsize=16)

        for dec in [-80, -70, -60, -50]:
            x, y = self.basemap(45, dec)
            self.ax.text(x, y, '%s$^{\circ}$' % dec, fontsize=16)

    def plot_prelim(self):
        """ Draw a label for unpublished plots. """
        x,y = self.basemap(45, -37)
        self.ax.text(x, y, 'IceCube Preliminary',
                     color='r', fontsize=14)

    def plot_galactic_plane(self):
        """ Plot the galactic plance region """

        cRot = hp.Rotator(coord = ['G','C'], rot = [0, 0])
        tl = np.radians(np.arange(0,360, 0.01))
        tb = np.radians(np.full(tl.size, 90))
        tdec, tra = np.degrees(cRot(tb,tl))
        x,y = self.basemap(tra, 90-tdec)
        sc  = self.basemap.plot(x, y, 'k--', linewidth=1, label='Galactic Plane')

        tb = np.radians(np.full(tl.size, 95))
        tdec, tra = np.degrees(cRot(tb,tl))
        x,y = self.basemap(tra, 90-tdec)
        sc  = self.basemap.plot(x, y, 'k-', linewidth=1)

        tb = np.radians(np.full(tl.size, 85))
        tdec, tra = np.degrees(cRot(tb,tl))
        x,y = self.basemap(tra, 90-tdec)
        sc  = self.basemap.plot(x, y, 'k-', linewidth=1)

    def plot_sky_map(self, sky_map, color_map,
                     neg_log=True, colorbar_label=None):
        """ Plot a sky map.
        Parameters
        ----------
        sky_map : numpy array
            A sky map in healpix format and in equatorial coordinates.
        color_map : matplotlib.colors.LinearSegmentedColormap
            a matplotlib colormap
        neg_log : boolean
            plot -log10(sky_map)
        colorbar_label : string
            label for the color bar.
        
        """
        sky_map = sky_map
        npix = len(sky_map)
        nside = hp.npix2nside(npix)
        dec, ra = np.degrees(hp.pix2ang(nside, range(npix)))

        if neg_log:
            sky_map = -np.log10(sky_map)

        x,y = self.basemap(ra, 90-dec)
        sc  = self.basemap.scatter(x, y, c=sky_map,
                                   vmin=0, vmax=4.5,
                                   cmap=color_map,
                                   s=2, lw=0, zorder=0,
                                   rasterized=True)

        if colorbar_label:
            clb = self.fig.colorbar(sc, orientation='vertical')
            clb.set_label(colorbar_label, fontsize=20)
