#!/usr/bin/env python

########################################################################
# Test of Galactic Plane Sensitivity   
########################################################################

import re
import argparse as ap
import numpy as np
import pandas as pd

from support_pandas import livetimes
from skylab_comp.template import Template
from skylab_comp.template_llh import TemplateLLH, MultiTemplateLLH
from skylab_comp.template_injector import TemplateInjector
from skylab_comp.llh_models import ClassicLLH, EnergyLLH

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
    args = p.parse_args()

    sinDec_range = [-1.,-0.8]
    sinDec_bins  = np.linspace(-1., -0.80, 21)
    energy_range = [5.5,8.5] # log(E/GeV)
    energy_bins  = [np.linspace(5.5,8.5,30), sinDec_bins]

    mc_years  = dict()
    lt_years  = dict()
    llh_model = dict()
    template_years = dict()
    template_llh = MultiTemplateLLH()

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

        llh_model[year] = EnergyLLH(twodim_bins=energy_bins,
                                    twodim_range=[energy_range,sinDec_range],
                                    sinDec_bins=sinDec_bins,
                                    sinDec_range=sinDec_range,
                                    bounds=[args.alpha, args.alpha],
                                    seed=1)

        year_llh = TemplateLLH(exp, mc, livetime,
                               scramble=True,
                               llh_model=llh_model[year],
                               template=template)

        template_llh.add_sample(year, year_llh)

    inj = TemplateInjector(template=template_years,
                           gamma=args.alpha,
                           E0=1000,
                           Ecut=None,
                           seed=1)
    inj.fill(exp, mc_years, lt_years)

    ab = [[0.5],[0.9]] # 90 percent upper limit.
    result, trials, weights = template_llh.weighted_sensitivity(alpha=ab[0],
                                                                beta=ab[1],
                                                                inj=inj,
                                                                #mc=mc_years,
                                                                eps=1.e-2,
                                                                n_bckg=10000,
                                                                n_iter=1000)

    print(result['flux'][0])
    np.save(args.prefix+args.name+'_sensitivity.npy', result['flux'][0])
