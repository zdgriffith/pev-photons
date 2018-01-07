#!/usr/bin/env python

########################################################################
# Write simple galactic plane template maps.
########################################################################

import argparse as ap
import numpy as np

import healpy as hp

from pev_photons.support import prefix

#Constant emission within some galactic latitude bound.
def box(args):
    npix  = hp.nside2npix(args.nside)
    nside = hp.npix2nside(npix)
    gal_lat,gal_lon = hp.pix2ang(nside, range(npix))
    m = np.zeros(npix)
    mask = np.less(np.abs(np.pi/2. - gal_lat),np.radians(args.size))
    m[mask] += 1
    np.save(prefix+('/galactic_plane/source_templates/'
                    'box_%s.npy' % args.size), m) 

# Ingelman-Thunman template, a thin constant plane region
# with an exponential decay beyond.
def ingelman_thunman(args):
    h_0 = 0.26
    d = 8.5
    theta_0 = np.arctan(h_0/d)

    npix = hp.nside2npix(args.nside)
    nside = hp.npix2nside(npix)
    gal_lat,gal_lon = hp.pix2ang(nside, range(npix))
    m = np.zeros(npix)
    mask = np.less(np.abs(np.pi/2. - gal_lat), theta_0)
    m[mask] += 1 
    m[~mask] += np.exp(-d*np.tan(np.abs(np.pi/2.-gal_lat[~mask]))/h_0)
    np.save(prefix+'/galactic_plane/source_templates/ingelman.npy', m) 

if __name__ == "__main__":
    p = ap.ArgumentParser(description='Build template maps.',
                          formatter_class=ap.RawTextHelpFormatter)
    p.add_argument('--size', type=float, default=5.0,
                   help='width of galactic plane in degrees.')
    p.add_argument('--nside', type=int, default=512,
                   help='Nside of the healpix map.')
    args = p.parse_args()

    box(args)
    ingelman_thunman(args)
