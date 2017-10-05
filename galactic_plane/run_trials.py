#!/usr/bin/env python

########################################################################
# Run background trials for checking the TS distributions.
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
    p.add_argument('--runTrial', action='store_true', default=False,
                   help='If True, run as a background trial.')
    p.add_argument('--verbose', action='store_true', default=False,
                   help='if True, print progress')
    p.add_argument('--job', type=int, default=0,
                   help='Job number for running on cluster')
    p.add_argument('--name', type = str, default='fermi_pi0',
                   help='name of the template')
    p.add_argument('--nTrials', type=int, default=100,
                   help='Number of trials to run with this job')
    p.add_argument('--n_inj', type=int, default=0,
                   help='Number of events to inject.')
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
                               scramble=args.runTrial,
                               llh_model=llh_model[year],
                               template=template)

        template_llh.add_sample(year, year_llh)

    if args.n_inj:
        inj = TemplateInjector(template=template_years,
                               gamma=args.alpha,
                               E0=1000,
                               Ecut=None,
                               seed=1)
        inj.fill(exp_years, mc_years, lt_years)

    if args.runTrial:
        trials = np.zeros(args.nTrials)
        for trial in range(args.nTrials):
            if args.verbose:
                print(trial)
            if args.n_inj:
                ni, sample = inj.sample(mean_signal=args.n_inj,
                                        poisson=False).next()
                trials[trial] = template_llh.fit_template_source(inject=sample,
                                                                 scramble=True)[0]
            else:
                trials[trial] = template_llh.fit_template_source(scramble=True)[0]
            if float(trial+1)%100 == 0:
                np.save('%s/galactic_plane/trials/%s_job_%s.npy' % (args.prefix, args.name, args.job), trials)
        np.save('%s/galactic_plane/trials/%s_job_%s.npy' % (args.prefix, args.name, args.job), trials)
    else:
        true = template_llh.fit_template_source(scramble=False)[0]
        print('True Stacking TS: '+str(true))
        np.save(args.prefix+args.name+'_TS.npy', true)
