#!/usr/bin/env python

########################################################################
# Calculates the true TS for each HESS source
########################################################################

import argparse
import numpy as np

from support_pandas import livetimes

from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH
from skylab.llh_models import EnergyLLH

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test HESS positions individually',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type = str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--outFile', type = str,
                   default='hess_sources_fit_results',
                   help='file name')
    p.add_argument('--extended', action='store_true', default=False,
                   help='If True, use source extension in fit.')
    args = p.parse_args()

    dec_bins = np.arange(-1., -0.799, 0.01)
    energy_bins = [np.linspace(5.7,8,24), dec_bins]

    #Initialization of multi-year LLH object
    psllh = MultiPointSourceLLH(ncpu=20)

    tot_mc = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']

    for i, year in enumerate(years): 
        livetime = livetimes(year)*1.157*10**-5  #Seconds to Days
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        mc = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')

        llh_model[year] = EnergyLLH(twodim_bins  = energy_bins,
                                    twodim_range = [[5.7,8],[-1,-0.8]],
                                    sinDec_bins  = dec_bins, sinDec_range=[-1,-0.8])

        year_psllh = PointSourceLLH(exp, mc, livetime,
                                    scramble=False,
                                    ncpu=20,
                                    llh_model=llh_model[year],
                                    mode='box',
                                    delta_ang=np.radians(10*0.4))
        psllh.add_sample(year, year_psllh)
        tot_mc[i] = mc 

    sources   = np.load(args.prefix+'TeVCat/hess_sources.npz')

    fit_arr = np.empty((len(sources['dec']),),
                       dtype=[('TS', np.float), ('nsources', np.float),
                              ('gamma', np.float)])
    
    for i, dec in enumerate(sources['dec']):
    
        if args.extended:
            out = psllh.fit_source(np.radians(sources['ra'][i]),
                                   np.radians(dec),
                                   src_extension=np.radians(sources['extent'])[i],
                                   scramble = False)
        else:
            out = psllh.fit_source(np.radians(sources['ra'][i]),
                                   np.radians(dec),
                                   scramble = False)

        fit_arr['TS'][i] = out[0]
        fit_arr['gamma'][i] = out[1]['gamma']
        fit_arr['nsources'][i] = out[1]['nsources']

    if args.extended:
        np.save(args.prefix+'TeVCat/extended/'+args.outFile+'.npy', fit_arr)
    else:
        np.save(args.prefix+'TeVCat/'+args.outFile+'.npy', fit_arr)
