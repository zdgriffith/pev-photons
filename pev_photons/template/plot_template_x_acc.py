#!/usr/bin/env python

########################################################################
# Plot a template PDF convolved with detector acceptance.
########################################################################

import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

import healpy as hp

from pev_photons import utils

if __name__ == "__main__":
    p = argparse.ArgumentParser(
                   description='Plot a template PDF convolved with detector acc.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--name', type = str,
                   default='fermi_pi0',
                   help='Name of the skymap to plot.')
    p.add_argument('--noPlane', action='store_true', default=False,
                   help='If True, do not draw galactic plane.')
    p.add_argument('--noGrid', action='store_true', default=False,
                   help='If True, do not draw grid lines.')
    p.add_argument('--year', type=str, default='2012',
                   help='Year of analyis to build.')
    args = p.parse_args()

    plt.style.use(utils.plot_style)

    fig, ax = plt.subplots(figsize=(12,8))

    skymap = utils.PolarSkyMap(fig, ax)

    if not args.noGrid:
        skymap.plot_grid()

    if not args.noPlane:
        skymap.plot_galactic_plane()

    filename = utils.prefix+'/template/'+args.year+'/'+args.name+'_exp.npy'
    hmap = np.load(filename)
    hmap = hp.ud_grade(hmap.item()['signal_x_acceptance_map'], nside_out=512)
    hmap = len(hmap)*hmap/np.sum(hmap[np.isfinite(hmap)])
    scatter_args = {'cmap':utils.plasma_map,
                    'norm':LogNorm(vmin=5*10**-2, vmax=np.max(hmap)),
                    's':2**3, 'lw':0, 'zorder':0, 'rasterized':True}

    skymap.plot_sky_map(hmap, coord='G', colorbar_label='Magnitude [A.U.]',
                        **scatter_args)

    ax.legend()
    plt.savefig(utils.fig_dir+'template/'+args.name+'_x_acc.png',
                bbox_inches='tight')
    if args.name == 'fermi_pi0':
        plt.savefig(utils.fig_dir+'paper/fermi_pi0_x_acc.pdf', bbox_inches='tight')
    plt.close()
