#!/usr/bin/env python

########################################################################
# Run background trials for galactic plane sensitivity calculation
########################################################################

import re
import sys
import argparse as ap
import numpy as np
import pandas as pd

from skylab_comp.sensitivity_utils import estimate_sensitivity
from support_pandas import livetimes
from skylab_comp.template import Template
from skylab_comp.template_llh import TemplateLLH, MultiTemplateLLH
from skylab_comp.template_injector import TemplateInjector
from skylab_comp.llh_models import ClassicLLH, EnergyLLH

def sensitivity(args):
    sinDec_range = [-1, -0.8]
    sinDec_bins = np.arange(-1.0, -0.799, 0.01)
    energy_range = [5.7, 8.0]
    energy_bins = [np.linspace(5.7,8,20), sinDec_bins]

    mc_years = dict()
    exp_years = dict()
    lt_years = dict()
    llh_model = dict()
    template_years = dict()
    template_llh = MultiTemplateLLH(ncpu=1)

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        template = Template((args.prefix+'/galactic_plane/'+year+'/'
                             + args.name+'_exp.npy'), reduced = True)

        livetime = livetimes(year)*1.157*10**-5  #Seconds to Days
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_diffuse.npy')
        mc  = np.load(args.prefix+'/datasets/'+year+'_mc_diffuse.npy')

        template_years[i] = template
        lt_years[i] = livetime 
        mc_years[i] = mc 
        exp_years[i] = exp

        llh_model[year] = EnergyLLH(twodim_bins=energy_bins,
                                    twodim_range=[energy_range,sinDec_range],
                                    sinDec_bins=sinDec_bins,
                                    sinDec_range=sinDec_range,
                                    fix_index=True,
                                    bounds=[args.alpha, args.alpha],
                                    seed=1)

        year_llh = TemplateLLH(exp, mc, livetime,
                               scramble=True,
                               llh_model=llh_model[year],
                               template=template)

        template_llh.add_sample(year, year_llh)

    inj = TemplateInjector(template=template_years,
                           gamma=args.alpha,
                           E0=2*10**6,
                           Ecut=None,
                           seed=1)
    inj.fill(exp_years, mc_years, lt_years)

    trials = template_llh.do_trials(args.n_trials, injector=inj,
                           mean_signal=args.n_inj)

    n = trials['TS'][ trials['TS'] > 0].size
    ntot = trials['TS'].size

    print ("ni %5.2f, n %4d, ntot %4d" % (args.n_inj, n, ntot)) 
    np.save("/data/user/zgriffith/pev_photons/galactic_plane/trials/"+args.name+"_job_"+str(args.job)+".npy", [args.n_inj, n, ntot])

if __name__ == "__main__":
    p = ap.ArgumentParser(description='Galactic plane sensitivity runs.',
                          formatter_class=ap.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='Base directory for file storing.')
    p.add_argument('--name', type=str, default='fermi_pi0',
                   help='The name of the template.')
    p.add_argument("--alpha", type=float, default=3.0,
                   help='Spectral index of signal.')
    p.add_argument("--n_inj", type=float, default=0,
                   help='Number of injected events')
    p.add_argument("--n_trials", type=int, default=100,
                   help='Number of trials')
    p.add_argument("--job", type=int, default=0,
                   help='job number')
    args = p.parse_args()

    sensitivity(args)
