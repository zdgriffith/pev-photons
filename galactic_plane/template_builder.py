#!/usr/bin/env python

########################################################################
## Build template maps for use in Skylab.
## Credit for the script goes to Josh Wood.
########################################################################

import os
import re
import argparse
import numpy as np

from skylab_comp.template import Template

def template_builder(args):
    """Build the template for a given year."""
    rad2deg = 180./np.pi
    deg2rad = 1./rad2deg

    exp = np.load(args.prefix+'/datasets/'+args.year+'_exp_diffuse.npy')
    mc  = np.load(args.prefix+'/datasets/'+args.year+'_mc_diffuse.npy')

    if args.mcBackground:
      ev  = mc
      ext = '_mc'
      weights = ['conv']
    else:
      ev  = exp
      ext = '_exp'
      weights = None

    output = (args.prefix + '/galactic_plane/' + args.year + '/' 
              + re.split('/|\.', args.inFile)[-2] + ext)

    os.system('mkdir -p ' + output)

    nbin = 20
    sinDec_min = -1
    sinDec_max = -0.8
    bin_width  = (sinDec_max - sinDec_min)/nbin
    sinDec_bins = np.arange(sinDec_min,
                            sinDec_max + 0.1*bin_width,
                            bin_width,
                            dtype=float)

    mask = (mc['sinDec'] > sinDec_min) & (mc['sinDec'] < sinDec_max)
    mc = mc[mask]
    mask = (exp['sinDec'] > sinDec_min) & (exp['sinDec'] < sinDec_max)
    exp = exp[mask]

    template = Template()

    template.build(map_in=args.prefix+args.inFile, nside_out=512,
                   coords='galactic',
                   mc=mc, exp=exp,
                   spline=True,
                   sinDec_bins=sinDec_bins,
                   weights=weights, # Set to None to use data in bg PDF.
                   gamma=args.alpha, # Spectral index of signal.
                   E0=1000, Ecut=None,
                   smoothings=np.arange(0.45, 1.05, 0.05),
                   selection=[-180,180,-90,90], selection_coords='galactic')

    template.display(output, 13, 3)
    template.write(output + '.npy')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Build template maps.',
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('--prefix', type = str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='Base directory for file storing.')
    p.add_argument('--mcBackground', action='store_true',
                    help=('Use MC to build background PDFs '
                          'and produce data scrambles.'))
    p.add_argument('--year', type=str, default='2012',
                   help=('Year of analyis to build. '
                         '"all" runs all years.'))
    p.add_argument('--inFile', type=str,
                   default='/galactic_plane/source_templates/fermi_pi0.npy',
                   help=('File containing the template '
                         'to use in healpix format.'))
    p.add_argument('--alpha', type=float, default=3.0,
                   help='Spectral index of signal.')
    args = p.parse_args()

    if args.year == 'all':
        for year in ['2011', '2012', '2013', '2014', '2015']:
            args.year = year
            template_builder(args)
    else:
        template_builder(args)
