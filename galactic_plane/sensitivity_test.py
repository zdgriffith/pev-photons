#!/usr/bin/env python

########################################################################
# Test the sensitivity to a galactic plane flux template. 
########################################################################

import argparse as ap
import numpy as np

from skylab.sensitivity_utils import estimate_sensitivity
from skylab.template_injector import TemplateInjector
from load_datasets import load_gp_dataset

def mu2flux(inj, args):

    print('dN/dE = %s' % inj.mu2flux(args.mu))
    conv = (args.Enorm**2)*inj.mu2flux(args.mu)
    print('E^2dN/dE = %s' % conv)

if __name__ == "__main__":
    p = ap.ArgumentParser(description='Test galactic plane sensitivity.',
                          formatter_class=ap.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='Base directory for file storing.')
    p.add_argument('--name', type=str, default='fermi_pi0',
                   help='The name of the template.')
    p.add_argument("--alpha", type=float, default=3.0,
                   help='Spectral index of signal.')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--Enorm", type=float, default=2*10**6,
                   help='normalization energy in GeV')
    p.add_argument("--mu", type=float, default=0.,
                   help='number of signal events')
    args = p.parse_args()

    template_llh = load_gp_dataset(args)

    inj = TemplateInjector(template=template_llh.template,
                           gamma=args.alpha,
                           E0=args.Enorm,
                           Ecut=None,
                           seed=1)
    inj.fill(template_llh.exp, template_llh.mc, template_llh.livetime)

    if args.mu:
        mu2flux(inj, args)

    #Directory where plots will go
    path = ("/home/zgriffith/public_html/"
            "photon_analysis/pev_photons/galactic_plane/"+args.name+"/")

    results = estimate_sensitivity(template_llh, inj,
                                   nstep=11, 
                                   ni_bounds=[0,2000], 
                                   nsample=100, 
                                   path=path)
