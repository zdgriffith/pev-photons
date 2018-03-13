#!/usr/bin/env python

########################################################################
# Test the sensitivity to a flux template. 
########################################################################

import argparse
import numpy as np

from skylab.sensitivity_utils import estimate_sensitivity, sensitivity_flux
from skylab.template_injector import TemplateInjector

from pev_photons.utils.load_datasets import load_systematic_dataset
from pev_photons.utils.support import fig_dir

def mu2flux(inj, args):

    print('dN/dE = %s' % inj.mu2flux(args.mu))
    conv = (args.Enorm**2)*inj.mu2flux(args.mu)
    print('E^2dN/dE = %s' % conv)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Test template sensitivity.',
                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--name', type=str, default='sybll',
                   help='The name of the template.')
    p.add_argument("--alpha", type=float, default=3.0,
                   help='Spectral index of signal.')
    p.add_argument("--Enorm", type=float, default=2*10**6,
                   help='normalization energy in GeV')
    p.add_argument("--mu", type=float, default=0.,
                   help='number of signal events')
    p.add_argument("--n_max", type=float, default=1000.,
                   help='maximum bound on injected signal events')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    exp, mc, livetime, template_llh, template = load_systematic_dataset('galactic_plane', args.name, args)

    inj = TemplateInjector(template=template,
                           gamma=args.alpha,
                           E0=args.Enorm,
                           Ecut=None,
                           seed=1)
    inj.fill(exp, mc, livetime)

    if args.mu:
        mu2flux(inj, args)

    #Directory where plots will go
    path = (fig_dir+'template/'+args.name+'/')

    results = estimate_sensitivity(template_llh, inj,
                                   nstep=11, 
                                   ni_bounds=[0,args.n_max], 
                                   nsample=100, 
                                   path=path)
