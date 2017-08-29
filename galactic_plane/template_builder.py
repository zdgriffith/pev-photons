#!/usr/bin/env python

###################################################
## Build template maps for use in skylab
## credit for script goes to Josh Wood
###################################################

import os, re
import numpy as np
from   skylab_comp.template import Template
import argparse

def template_builder(prefix, inFile, year, mcBackground, alpha):
    rad2deg = 180./np.pi
    deg2rad =   1./rad2deg

    exp = np.load(prefix+'/datasets/'+year+'_exp_diffuse.npy')
    mc  = np.load(prefix+'/datasets/'+year+'_mc_diffuse.npy')

    if mcBackground:
      ev = mc
      weights = ['conv']
      ext = "_mc"
    else:
      ev = exp
      weights = None
      ext = "_exp"

    output = prefix+'/galactic_plane/'+year+'/'+re.split("/|\.", inFile)[-2]+ext

    os.system("mkdir -p " + output)

    sinDec_min   = -1
    sinDec_max   = -0.8
    nbin         = 20
    bin_width    = (sinDec_max - sinDec_min)/nbin
    sinDec_bins  = np.arange(sinDec_min,
                                sinDec_max+0.1*bin_width,
                                bin_width,
                                dtype=float)

    mask = (mc['sinDec'] > sinDec_min) & (mc['sinDec'] < sinDec_max)
    mc = mc[mask]

    mask = (exp['sinDec'] > sinDec_min) & (exp['sinDec'] < sinDec_max)
    exp = exp[mask]

    template = Template()

    template.build(map_in           = prefix+inFile,
                   coords           = 'galactic',
                   exp              = exp,
                   mc               = mc,
                   spline           = True,
                   sinDec_bins      = sinDec_bins,
                   weights          = weights, # set to None to use data in background PDF
                   gamma            = alpha,       # spectral index of signal dN/dE = A (E / E0)^-gamma
                   E0               = 1000,
                   Ecut             = None,
                   nside_out        = 1024,
                   smoothings       = np.arange(0.45, 1.05, 0.05),
                   selection        = [-180,180,-90,90],
                   selection_coords = 'galactic')

    template.display(output, 13, 3)
    template.write(output + ".npy")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Build Template maps",
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument("--mcBackground", action='store_true',
                    help="Use MC to build background PDFs and produce data scrambles")
    p.add_argument('--year', dest='year', type = str,
                   help='Year', default = '2012')
    p.add_argument('--inFile', dest='inFile', type = str,
                   default = '/galactic_plane/source_templates/fermi_pi0.npy',
                   help    = 'file containing the template to use in healpix format')
    p.add_argument('-a', '--alpha', dest='alpha', type = float,
                   help='Spectral Index', default = 3.0)

    args = p.parse_args()

    if args.year == 'all':
        for year in ['2011','2012','2013','2014','2015']:
            template_builder(args.prefix, args.inFile, year, args.mcBackground, args.alpha)
    else:
        template_builder(args.prefix, args.inFile, args.year, args.mcBackground, args.alpha)
