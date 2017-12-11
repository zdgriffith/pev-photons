#!/usr/bin/env python

########################################################################
# Runs a stacking test of the HESS source catalog.
########################################################################

import argparse
import numpy as np

from support_pandas import livetimes

from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH
from skylab.llh_models import EnergyLLH

def run_bg_trials(psllh, sources, args):
    trials = psllh.do_trials(args.bg_trials, src_ra=np.radians(sources['ra']),
                             src_dec=np.radians(sources['dec']))
    np.save(args.prefix+'TeVCat/stacking_trials.npy', trials['TS'])

def run_stacking_test(psllh, sources, args):
    fit_arr = np.empty((1,),
                       dtype=[('TS', np.float), ('nsources', np.float),
                              ('gamma', np.float)])
    if args.extended:
        out = psllh.fit_source(np.radians(sources['ra']),
                               np.radians(sources['dec']),
                               src_extension=np.radians(sources['extent']),
                               scramble=False)
    else:
        out = psllh.fit_source(np.radians(sources['ra']),
                               np.radians(sources['dec']),
                               scramble=False)
    fit_arr['TS'][0] = out[0]
    fit_arr['gamma'][0] = out[1]['gamma']
    fit_arr['nsources'][0] = out[1]['nsources']
    
    if args.extended:
        np.save(args.prefix+'TeVCat/extended/stacking_fit_result.npy', fit_arr)
    else:
        np.save(args.prefix+'TeVCat/stacking_fit_result.npy', fit_arr)

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Runs a stacking test of the HESS source catalog.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--bg_trials', type=float, default=0,
                   help='if nonzero, run this number of background trials')
    p.add_argument('--extended', action='store_true', default=False,
                   help='If True, use source extension in fit.')
    args = p.parse_args()

    sinDec_range = [-1.,-0.8]
    sinDec_bins  = np.linspace(-1.,-0.8, 21)
    energy_range = [5.7,8] # log(E/GeV)
    energy_bins  = [np.linspace(5.7,8,24), sinDec_bins]

    psllh = MultiPointSourceLLH(ncpu=20)
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        livetime = livetimes(year)*1.157*10**-5  # Convert seconds to days.
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        exp['dec'] = np.arcsin(exp['sinDec'])
        mc  = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')
        mc['dec'] = np.arcsin(mc['sinDec'])

        llh_model[year] = EnergyLLH(twodim_bins=energy_bins,
                                    twodim_range=[[5.7,8],[-1,-0.8]],
                                    sinDec_bins=sinDec_bins,
                                    sinDec_range=[-1,-0.8])

        year_psllh = PointSourceLLH(exp, mc, livetime,
                                    ncpu=20,
                                    scramble=False,
                                    llh_model=llh_model[year],
                                    delta_ang=np.radians(10*0.4))

        psllh.add_sample(year, year_psllh)

    sources = np.load(args.prefix+'/TeVCat/hess_sources.npz')
    if args.bg_trials:
        run_bg_trials(psllh, sources, args)
    else:
        run_stacking_test(psllh, sources, args)
