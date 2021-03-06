#!/usr/bin/env python

########################################################################
# Build template maps for use in Skylab.
# Credit for the script goes to Josh Wood.
########################################################################

import argparse
import os
import re
import numpy as np

from skylab.datasets import Datasets
from skylab.template import Template
from pev_photons.utils.support import prefix, resource_dir, fig_dir

def template_builder(args):
    """Build the template for a given year."""
    rad2deg = 180./np.pi

    livetimes = {'2011': 26673776.,
                 '2012': 25569773.,
                 '2013': 27769791.,
                 '2014': 28139667.,
                 '2015': 28097975.}

    if 'Laputop' in args.model:
        exp = np.load(prefix+'/datasets/systematics/skylab/{}/{}_exp_diffuse.npy'.format(args.year, args.model))
        livetime = 0.05*livetimes[args.year]*1.157*10**-5 # days
    else:
        exp = np.load(prefix+'/resources/datasets/{}_exp_diffuse.npy'.format(args.year))
        livetime = livetimes[args.year]*1.157*10**-5 # days

    mc = np.load(prefix+'/datasets/systematics/skylab/{}/{}_mc_diffuse.npy'.format(args.year, args.model))


    if args.mcBackground:
      ev  = mc
      ext = '_mc'
      weights = ['conv']
    else:
      ev  = exp
      ext = '_exp'
      weights = None

    output = (prefix + '/template/' + args.year + '/' 
              + args.model + ext)
    fig_out = (fig_dir + '/template/' + args.year + '/' 
               + args.model + ext)

    os.system('mkdir -p ' + output)
    os.system('mkdir -p ' + fig_out)
    sinDec_min = -1
    sinDec_max = -0.8
    sinDec_bins = np.linspace(-1., -0.80, 21)

    mask = (mc['sinDec'] > sinDec_min) & (mc['sinDec'] < sinDec_max)
    mc = mc[mask]
    mask = (exp['sinDec'] > sinDec_min) & (exp['sinDec'] < sinDec_max)
    exp = exp[mask]

    template = Template()

    template.build(map_in=(resource_dir + args.inFile + '.npy'),
                   nside_out=512,
                   mc=mc, exp=exp,
                   coords='galactic',
                   spline=True,
                   sinDec_bins=sinDec_bins,
                   weights=weights, # Set to None to use data in bg PDF.
                   gamma=args.alpha, # Spectral index of signal.
                   E0=1000, Ecut=None,
                   smoothings=np.arange(0.45, 1.05, 0.05),
                   selection=[-180,180,-90,90], selection_coords='galactic')

    template.display(fig_out, 13, 3)
    template.write(output + '.npy')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Build template maps.',
                   formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('--mcBackground', action='store_true',
                    help=('Use MC to build background PDFs '
                          'and produce data scrambles.'))
    p.add_argument('--year', type=str, default='2012',
                   help=('Year of analyis to build. '
                         '"all" runs all years.'))
    p.add_argument('--inFile', type=str,
                   default='fermi_pi0',
                   help=('File containing the template '
                         'to use in healpix format.'))
    p.add_argument('--model', type=str, default='sybll',
                   help='The name of the hadronic interaction model.')
    p.add_argument('--alpha', type=float, default=3.0,
                   help='Spectral index of signal.')
    args = p.parse_args()

    if args.year == 'all':
        for year in ['2011', '2012', '2013', '2014', '2015']:
            args.year = year
            template_builder(args)
    else:
        template_builder(args)
