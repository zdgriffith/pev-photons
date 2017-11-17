#!/usr/bin/env python

#############################################
####   Stacking Test of HESS Catalog   ######
#############################################

import argparse
import numpy as np
import pandas as pd

from support_pandas import livetimes

from skylab_mhuber.psLLH import StackingPointSourceLLH,StackingMultiPointSourceLLH
from skylab_mhuber.ps_model import ClassicLLH, EnergyLLH

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
    p.add_argument('--nTrials', dest='nTrials', type = int,
                   default = 100,
                   help='Number of trials to run with this job')
    args = p.parse_args()

    sinDec_range = [-1.,-0.8]
    sinDec_bins  = np.arange(-1., -0.799, 0.01)
    energy_range = [5.5,8.5] # log(E/GeV)
    energy_bins  = [np.linspace(5.5,8.5,30), sinDec_bins]

    psllh = StackingMultiPointSourceLLH(delta_ang = np.radians(10*0.4))
    tot_mc    = dict()
    llh_model = dict()

    years     = ['2011', '2012', '2013', '2014','2015']

    for i, year in enumerate(years): 
        livetime    = livetimes(year)*1.157*10**-5  #Seconds to Days
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        mc  = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')
        llh_model[year] = EnergyLLH(twodim_bins  = energy_bins,
                                    twodim_range = [energy_range,sinDec_range],
                                    sinDec_bins  = sinDec_bins, sinDec_range=sinDec_range)

        year_psllh = StackingPointSourceLLH(exp, mc, livetime,
                               scramble  = args.runTrial,
                               llh_model = llh_model[year],
                               delta_ang = np.radians(10*0.4), #Recommended ~10 times ang_res
                               )
        psllh.add_sample(year, year_psllh)
        tot_mc[i] = mc 

    pos = np.load(args.prefix+'/TeVCat/hess_sources.npz')

    ra  = []
    dec = []
    for i, deci in enumerate(pos['dec']):
        ra.append(pos['ra'][i])
        dec.append(pos['dec'][i])

    if args.runTrial:
        stack_trials = np.zeros(args.nTrials)
        for trial in range(args.nTrials):
            if args.verbose:
                print(trial)
            stack_trials[trial] = psllh.fit_source(np.radians(ra),np.radians(dec), scramble = True)[0]
        np.save(args.prefix+'/TeVCat/stacking_trials/job_%s.npy' % args.job, stack_trials)
    else:
        stack_true = psllh.fit_source(np.radians(ra),np.radians(dec), scramble=False)[0]
        print('True Stacking TS: '+str(stack_true))
        np.save(args.prefix+'TeVCat/stacking_TS.npy', stack_true)
