#!/usr/bin/env python

########################################################################
# Plot FOVs of experiments sensitive to diffuse PeV photons
# Translated from original script by Hershal Pandya
########################################################################

import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.spatial import ConvexHull

import healpy as hp
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates import Angle as astropyAngle

from pev_photons import utils

def move_gc_to_center(lon):
    l_t=astropyAngle(lon*u.radian)
    l_t=l_t.wrap_at(180.*u.deg).radian
    return l_t

def get_fermi_pi0_map():
    fermi = np.load(utils.resource_dir+'fermi_pi0.npy')

    eq_map = hp.cartview(fermi, return_projected_map=True)
    plt.close()

    newfermi = hp.ud_grade(map_in=fermi,nside_out=256)
    newmap = hp.cartview(newfermi, min=1e-2, norm='log',
                         cmap='jet', return_projected_map=True)
    plt.close()

    return newmap

def plot_IC_FOV(ax, config='86'):
    """ Plot the Icecube FOV for different configurations. """
    params = {'max_dec': {'86':np.arccos(0.8), '40': np.radians(30)},
              'color': {'86':colors[1], '40': colors[0]},
              'y': {'86':11, '40': -55.5}}

    dec, ra = np.meshgrid(np.linspace(0., params['max_dec'][config], 100) - np.pi/2.,
                          np.linspace(0., 2.0*np.pi, 1000))
    dec = dec.flatten()
    ra = ra.flatten()
    c = SkyCoord(ra=ra*u.radian, dec=dec*u.radian, frame='fk5')
    latFOV = c.galactic.b.degree
    lonFOV = np.degrees(move_gc_to_center(c.galactic.l.radian))
    points = np.array([ [lonFOV[i], latFOV[i]] for i in range(len(lonFOV))])
    hull = ConvexHull(points)
    ax.plot(points[hull.vertices,0], points[hull.vertices,1],
            c=params['color'][config], lw=2, ls='--')
    ax.text(x=-50, y=params['y'][config],
            s='IC-{}'.format(config), color=params['color'][config],
            fontsize=30, fontweight='bold')

def plot_rectangular_FOV(ax, exp='cm'):
    """ Plot the FOV for other experiments. """
    params = {'lon': {'cm': [50, 200], 'argo': [25, 100], '40': [285, 320]},
              'color': {'cm':'lawngreen', 'argo': 'magenta', '40':colors[0]},
              'x': {'cm': 150, 'argo': 75, '40':-50},
              'y': {'cm': 7, 'argo': 7, '40':-55.5},
              'label': {'cm': 'CASA-MIA', 'argo': 'ARGO-YBJ', '40':'IC-40'}}

    lon1 = move_gc_to_center(params['lon'][exp][0]*np.pi/180.)*180./np.pi
    lon2 = move_gc_to_center(params['lon'][exp][1]*np.pi/180.)*180./np.pi
    ax.plot([lon1, lon1], [-5, 5], lw=2,
            c=params['color'][exp], ls='--')
    ax.plot([lon2, lon2], [-5, 5], lw=2,
            c=params['color'][exp], ls='--')

    if exp == 'cm':
        ax.plot([lon2, -180], [-5, -5], lw=2,
                c=params['color'][exp], ls='--')
        ax.plot([lon2, -180], [5, 5], lw=2,
                c=params['color'][exp], ls='--')
        ax.plot([lon1, 180], [5, 5], lw=2,
                c=params['color'][exp], ls='--')
        ax.plot([lon1, 180], [-5, -5], lw=2,
                c=params['color'][exp], ls='--')
    else:
        ax.plot([lon1, lon2], [-5, -5], lw=2,
                c=params['color'][exp], ls='--')
        ax.plot([lon1, lon2], [5, 5], lw=2,
                c=params['color'][exp], ls='--')
    ax.text(x=params['x'][exp], y=params['y'][exp],
            s=params['label'][exp], color=params['color'][exp],
            fontsize=30, fontweight='bold')

if __name__ == "__main__":

    plt.style.use(utils.plot_style)
    fig, ax = plt.subplots(figsize=(20,10))
    colors = plt.rcParams['axes.color_cycle']

    im = ax.imshow(get_fermi_pi0_map(), extent=[180,-180,-90,90], origin='lower',
                   interpolation='none', cmap='Greys', norm=LogNorm())

    plot_IC_FOV(ax, config='40')
    plot_IC_FOV(ax, config='86')
    plot_rectangular_FOV(ax, exp='cm')
    plot_rectangular_FOV(ax, exp='argo')

    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)
    ax.set_xlim([180, -180])
    ax.set_ylim([-90, 90])
    ax.set_xlabel('Galactic Longitude [$^{\circ}$]', fontsize=30)
    ax.set_ylabel('Galactic Latitude [$^{\circ}$]', fontsize=30)

    plt.savefig(utils.fig_dir+'template/FOV_comparison.png')
    plt.savefig(utils.fig_dir+'paper/FOV_comparison.pdf')
