#!/usr/bin/env python

#############################################
####   Stacking Test of HESS Catalog   ######
#############################################

import argparse
import numpy as np
import pandas as pd

from support_pandas import livetimes

from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH
from skylab.llh_models import ClassicLLH, EnergyLLH

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Stacking Test',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--runTrial', dest='runTrial', action = 'store_true',
                   default = False, help='if True, run as a background trial')
    p.add_argument('--verbose', dest='verbose', action = 'store_true',
                   default = False, help='if True, print progress')
    p.add_argument('--job', dest='job', type = int,
                   default = 0,
                   help='Job number for running on cluster')
    p.add_argument('--n_trials', dest='n_trials', type = int,
                   default = 100,
                   help='Number of trials to run with this job')
    args = p.parse_args()

    sinDec_range = [-1.,-0.8]
    sinDec_bins  = np.arange(-1., -0.799, 0.01)
    sinDec_bins  = np.linspace(-1.,-0.8, 21)
    energy_range = [5.7,8] # log(E/GeV)
    energy_bins  = [np.linspace(5.7,8,24), sinDec_bins]

    psllh = MultiPointSourceLLH(ncpu=20)
    tot_mc = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        livetime = livetimes(year)*1.157*10**-5  # Convert seconds to days.
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        exp['dec'] = np.arcsin(exp['sinDec'])
        mc  = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')
        mc['dec'] = np.arcsin(mc['sinDec'])

        llh_model[year] = EnergyLLH(twodim_bins=energy_bins,
                                    twodim_range=[[5.5,8.5],[-1,-0.8]],
                                    sinDec_bins=sinDec_bins,
                                    sinDec_range=[-1,-0.8])

        year_psllh = PointSourceLLH(exp, mc, livetime,
                                    ncpu=20,
                                    scramble=False,
                                    llh_model=llh_model[year],
                                    delta_ang=np.radians(10*0.4))

        psllh.add_sample(year, year_psllh)
        tot_mc[i] = mc 

    pos = np.load(args.prefix+'/TeVCat/hess_sources.npz')
    ra = pos['ra']
    dec = pos['dec']

    if args.runTrial:
        trials = psllh.do_trials(args.n_trials, src_ra=np.radians(ra),
                                 src_dec=np.radians(dec))
        np.save(args.prefix+'TeVCat/stacking_trials.npy', trials['TS'])
    else:
        stack_true = psllh.fit_source(np.radians(ra),np.radians(dec), scramble=False)[0]
        print('True Stacking TS: '+str(stack_true))
        np.save(args.prefix+'TeVCat/stacking_TS.npy', stack_true)
