#!/usr/bin/env python

########################################################################
# Run the galactic plane correlation analysis
########################################################################

import argparse
import numpy as np
import pandas as pd

from support_pandas import livetimes
from skylab_comp.template import Template
from skylab_comp.template_llh import TemplateLLH, MultiTemplateLLH
from skylab_comp.template_injector import TemplateInjector
from skylab_comp.llh_models import ClassicLLH, EnergyLLH

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='galactic plane test',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='Base directory for file storing.')
    p.add_argument('--name', type = str, default='fermi_pi0',
                   help='name of the template')
    p.add_argument("--alpha", type=float, default=3.0,
                    help="Power law index")
    args = p.parse_args()

    sinDec_range = [-1, -0.8]
    sinDec_bins = np.arange(-1.0, -0.799, 0.01)
    energy_range = [5.7, 8.0]
    energy_bins = [np.linspace(5.7,8,20), sinDec_bins]

    template_llh = MultiTemplateLLH()
    template_years = dict()
    exp_years = dict()
    mc_years = dict()
    lt_years = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']

    for i, year in enumerate(years): 
        template = Template((args.prefix+'/galactic_plane/'+year
                             '/'+args.name+'_exp.npy'),
                            reduced=True)
        livetime = livetimes(year)*1.157*10**-5  #Seconds to Days
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_diffuse.npy')
        mc = np.load(args.prefix+'/datasets/'+year+'_mc_diffuse.npy')

        template_years[i] = template
        lt_years[i] = livetime 
        mc_years[i] = mc 
        exp_years[i] = exp

        llh_model[year] = EnergyLLH(twodim_bins=energy_bins,
                                    twodim_range=[energy_range,sinDec_range],
                                    seed=1,
                                    bounds=[args.alpha, args.alpha],
                                    fix_index=True,
                                    sinDec_bins=sinDec_bins,
                                    sinDec_range=sinDec_range)

        year_llh = TemplateLLH(exp, mc, livetime,
                               scramble=False,
                               llh_model=llh_model[year],
                               template=template)

        template_llh.add_sample(year, year_llh)

    true = template_llh.fit_template_source(scramble=False)[0]
    print('True Stacking TS: '+str(true))
    np.save(args.prefix+args.name+'_TS.npy', true)
