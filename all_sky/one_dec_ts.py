#!/usr/bin/env python

########################################################################
# Calculates the TS for a given declination
########################################################################

import argparse
import numpy as np
import pandas as pd

from support_pandas import get_fig_dir, livetimes
fig_dir = get_fig_dir()

from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH
from skylab.llh_models import ClassicLLH, EnergyLLH

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test hotspot',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument("--n_trials", type=int, default=100,
                   help='Number of trials')
    p.add_argument("--dec_i", type=int, default=0,
                   help='index corresponding to a declination in array')
    p.add_argument("--job", type=int, default=0,
                   help='job number')
    args = p.parse_args()

    dec_bins = np.linspace(-1., -0.8, 21)
    energy_bins = [np.linspace(5.7,8,24), dec_bins]

    #Initialization of multi-year LLH object
    psllh = MultiPointSourceLLH()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']

    for i, year in enumerate(years): 
        livetime = livetimes(year)*1.157*10**-5  #Seconds to Days
        exp      = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        mc       = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')

        llh_model[year] = EnergyLLH(twodim_bins  = energy_bins,
                                    twodim_range = [[5.5,8.5],[-1,-0.8]],
                                    sinDec_bins  = dec_bins, sinDec_range=[-1,-0.8])

        year_psllh = PointSourceLLH(exp, mc, livetime,
                               scramble  = False,
                               llh_model = llh_model[year],
                               mode      = 'box',
                               delta_ang = np.radians(10*0.4), #Recommended ~10 times ang_res
                               )
        psllh.add_sample(year, year_psllh)

    decs = np.load(args.prefix+'all_sky/dec_values_512.npz')['decs']

    trials = psllh.do_trials(args.n_trials, src_ra=np.pi,
                             src_dec=decs[args.dec_i])
    np.save(args.prefix+'all_sky/dec_trials/dec_%s_job_%s.npy' % (args.dec_i, args.job), trials['TS'])
