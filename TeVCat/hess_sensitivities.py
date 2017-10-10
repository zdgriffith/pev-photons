#!/usr/bin/env python

########################################################################
# Calculates the sensitivity to each HESS source's
# declination and spectral index 
########################################################################


import argparse
import numpy as np
import pandas as pd

from support_pandas import get_fig_dir, livetimes
fig_dir = get_fig_dir()

from skylab import psLLH
from skylab.psLLH import PointSourceLLH,MultiPointSourceLLH
from skylab.ps_injector import PointSourceInjector
from skylab.ps_model import ClassicLLH, EnergyLLH

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Calculate sensitivity to HESS sources',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    args = p.parse_args()

    dec_bins    = np.arange(-1., -0.799, 0.01)
    energy_bins = [np.linspace(5.5,8.5,30), dec_bins]

    #Initialization of multi-year LLH object
    psllh = MultiPointSourceLLH(ncpu      = 20,
                                mode      = 'box',
                                delta_ang = np.radians(10*0.4), #Recommended ~10 times ang_res
                                nside     = 128
                                )
    tot_mc    = dict()
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
                               ncpu      = 20,
                               llh_model = llh_model[year],
                               mode      = 'box',
                               delta_ang = np.radians(10*0.4), #Recommended ~10 times ang_res
                               nside     = 128,
                               )
        psllh.add_sample(year, year_psllh)
        tot_mc[i] = mc 

    sources   = np.load(args.prefix+'TeVCat/hess_sources.npz')

    ab   = [[0.5, 3*10**-7],[0.9,0.5]]
    sens = np.zeros((len(sources['dec']), 2))

    for j, dec in enumerate(sources['dec']):
        inj = PointSourceInjector(sources['alpha'][j], GeV = 10**3, E0 = 10**3,
                                  sinDec_bandwidth=np.sin(np.radians(2)))
        flux = psllh.weighted_sensitivity(src_ra = np.pi, src_dec = np.radians(float(dec)),
                                          alpha = ab[0], beta = ab[1], inj = inj, mc = tot_mc,
                                          eps=1.e-2,
                                          n_bckg = 10000,
                                          n_iter = 1000)
        sens[j] += flux['flux']


    a = {}
    a['sensitivity']         = sens.T[0]
    a['discovery_potential'] = sens.T[1]
    for key in sources.keys():
        a[key] = sources[key]

    np.savez(args.prefix+'TeVCat/hess_sources.npz', **a)
