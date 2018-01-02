#!/usr/bin/env python

########################################################################
# Perform a sensitivity calculation fit on injected trials distributions
########################################################################

import numpy as np
from glob import glob
import argparse as ap

from skylab.sensitivity_utils import fit
from skylab.template_injector import TemplateInjector
from load_datasets import load_gp_dataset

from support_functions import get_fig_dir
fig_dir = get_fig_dir()

def sensitivity(args):
    template_llh = load_gp_dataset(args)

    inj = TemplateInjector(template=template_llh.template,
                           gamma=args.alpha,
                           E0=args.E0,
                           Ecut=None,
                           seed=1)
    inj.fill(template_llh.exp, template_llh.mc, template_llh.livetime)

    files = glob(args.prefix+'galactic_plane/sens_trials/*.npy') 
    inj_list =[20.,   98.,  176.,  254.,  332.,  410.,
               488.,  566.,  644., 722.,  800.]

    frac = np.zeros(len(inj_list))
    tot = np.zeros(len(inj_list))
    for fname in files:
        a = np.load(fname)
        index = inj_list.index(a[0])
        frac[index] += a[1]
        tot[index] += a[2]
        
    ni, ni_err, images = fit(inj_list, frac, tot,
                             0.9, ylabel="fraction TS > 0.90",
                             npar = 2, par = None,
                             image_base=fig_dir+'fermi_pi0_sens')
    flux = inj.mu2flux(ni)
    flux_err = flux * ni_err / ni

    print ("  ni ------------  %.2f +/- %.2f (p %.2f)" % (ni, ni_err, 0.9))
    print ("  flux ----------  %.2e +/- %.2e GeV^-1cm^-2s^-1\n" % (flux, flux_err))

    sens_result = np.empty((1,),
                           dtype=[('ni', np.float), ('ni_err', np.float),
                                  ('flux', np.float), ('flux_err', np.float),
                                 ])

    sens_result['ni'] = ni
    sens_result['ni_err'] = ni_err
    sens_result['flux'] = flux
    sens_result['flux_err'] = flux_err
    np.save(args.prefix+'galactic_plane/fermi_pi0_sens.npy', sens_result)

if __name__ == "__main__":
    p = ap.ArgumentParser(description='Perform a sensitivity calculation fit',
                          formatter_class=ap.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='Base directory for file storing.')
    p.add_argument('--name', type=str, default='fermi_pi0',
                   help='The name of the template.')
    p.add_argument("--alpha", type=float, default=3.0,
                   help='Spectral index of signal.')
    p.add_argument("--E0", type=float, default=2e6,
                   help='Energy to normalize.')
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    sensitivity(args)
